import type { ValueOf } from 'type-fest'
import { createResponseJSON } from '@/utils/api'
import { BING_DOMAIN, db } from '@/utils/database'
import { type NextRequest, NextResponse } from 'next/server'
import random from 'random'

const TYPES = {
  ALL: 0,
  DAILY_WALLPAPER: 1,
  TRENDING_IMAGES: 2,
}

const LANGS: {
  EN_US: 'en-US'
  ZH_CN: 'zh-CN'
} = {
  EN_US: 'en-US',
  ZH_CN: 'zh-CN',
}

enum MODE {
  DATA = 'data',
  IMAGE = 'image',
}

export function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams

  let type = Number(searchParams.get('type') ?? TYPES.DAILY_WALLPAPER)
  if (!Object.values(TYPES).includes(type)) {
    type = TYPES.DAILY_WALLPAPER
  }

  let lang = (searchParams.get('lang') ?? LANGS.EN_US) as ValueOf<typeof LANGS>
  if (!Object.values(LANGS).includes(lang)) {
    lang = LANGS.EN_US
  }

  let mode = (searchParams.get('mode') ?? MODE.DATA) as ValueOf<typeof MODE>
  if (!Object.values(MODE).includes(mode)) {
    mode = MODE.DATA
  }

  const imagesMap = new Map<string, string>()
  if ([TYPES.ALL, TYPES.DAILY_WALLPAPER].includes(type)) {
    db.dailyWallpaper[lang].forEach((bucket) => {
      bucket.data.forEach((item) => {
        imagesMap.set(BING_DOMAIN + item.url, item.title)
      })
    })
  }
  if ([TYPES.ALL, TYPES.TRENDING_IMAGES].includes(type)) {
    db.trendingImages[lang].forEach((data) => {
      data.tiles.forEach((image) => {
        imagesMap.set(image.image.contentUrl, image.query.displayText)
      })
    })
  }

  const urls = Array.from(imagesMap, ([url, alt]) => ({ url, alt }))
  const index = random.integer(0, urls.length - 1)

  if (mode === MODE.IMAGE) {
    return NextResponse.redirect(urls[index].url, 307)
  }

  return createResponseJSON(urls[index])
}

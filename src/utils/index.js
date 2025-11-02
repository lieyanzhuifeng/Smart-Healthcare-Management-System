/**
 * 格式化日期
 */
export function formatDate(date, format = "YYYY-MM-DD HH:mm:ss") {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, "0")
  const day = String(d.getDate()).padStart(2, "0")
  const hour = String(d.getHours()).padStart(2, "0")
  const minute = String(d.getMinutes()).padStart(2, "0")
  const second = String(d.getSeconds()).padStart(2, "0")

  return format
    .replace("YYYY", year)
    .replace("MM", month)
    .replace("DD", day)
    .replace("HH", hour)
    .replace("mm", minute)
    .replace("ss", second)
}

/**
 * 防抖函数
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 */
export function throttle(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) return
    timer = setTimeout(() => {
      fn.apply(this, args)
      timer = null
    }, delay)
  }
}

/**
 * 深拷贝
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== "object") return obj
  if (obj instanceof Date) return new Date(obj)
  if (obj instanceof Array) return obj.map((item) => deepClone(item))

  const cloneObj = {}
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloneObj[key] = deepClone(obj[key])
    }
  }
  return cloneObj
}

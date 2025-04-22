importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.4/full/pyodide.js')
importScripts('https://cdn.jsdelivr.net/npm/xhr-shim@0.1.3/src/index.min.js')

self.XMLHttpRequest = self.XMLHttpRequestShim

let PYODIDE = null
let LOADED = 0
let LOCK = null

const COOKIES = {}
const PRJ_NAME = new URL(location).searchParams.get('PRJ_NAME')
const HOST = new URL(location).searchParams.get('HOST')

var PYTIGON_INIT = `
print("PYTIGON_INIT - B1")
import os
import pyodide.http
import json
print("PYTIGON_INIT - B2")

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ["SECRET_KEY"] = "anawa"
os.environ["PYTIGON_DEBUG"] = "false"
os.environ["MAILER"] = "false"
os.environ["PYTIGON_PASSWORD_HASHERS"] = "['django.contrib.auth.hashers.BCryptSHA256PasswordHasher']"
os.environ["PUBLISH_IN_SUBFOLDER"] = "_" 
#os.environ["PWA"] = "true" 
print("PYTIGON_INIT - B3")

if not os.path.exists("/home/pyodide/pytigon_data/{{PRJ_NAME}}/{{PRJ_NAME}}.db"):
    #os.makedirs("/home/pyodide/pytigon_data/{{PRJ_NAME}}", exist_ok=True)  
    #res = await pyodide.http.pyfetch("{{HOST}}/data/{{PRJ_NAME}}.db")
    #with open("/home/pyodide/pytigon_data/{{PRJ_NAME}}/{{PRJ_NAME}}.db", "wb") as out:
    #    out.write(await res.bytes())

    res = await pyodide.http.pyfetch("{{HOST}}/install/{{PRJ_NAME}}.ptig")
    ptig_installer = await res.bytes()
else:
    ptig_installer = None


print("PYTIGON_INIT - B4")

from pytigon.pytigon_request import init, request
print("PYTIGON_INIT - B5")

if ptig_installer:
    init("{{PRJ_NAME}}", "{{USER}}", "{{PASSWORD}}", user_agent="WebKit",  ptig_installer=ptig_installer)
else:
    init("{{PRJ_NAME}}", "{{USER}}", "{{PASSWORD}}", user_agent="WebKit")
print("PYTIGON_INIT - B6")

from django.conf import settings
print("PYTIGON_INIT - B7")

def request2(url, params=None):
    return request(url, params, "webview")
`

class AsyncLock {
  constructor () {
    this.disable = () => {}
    this.promise = Promise.resolve()
  }

  enable () {
    this.promise = new Promise(resolve => (this.disable = resolve))
  }
}

callback_func = function (err) {
  if (err) {
    console.error(err)
  }
}

async function installPython () {
  await PYODIDE.loadPackage('micropip')
  await PYODIDE.loadPackage('aiohttp')
  await PYODIDE.loadPackage('multidict')
  await PYODIDE.loadPackage('sqlite3')
  await PYODIDE.loadPackage('tzdata')
  const micropip = PYODIDE.pyimport('micropip')
  await micropip.install('lzma')
  await micropip.install(`${HOST}/wheel/http_ece-1.2.1-py2.py3-none-any.whl`)
  await micropip.install('pytigon-lib')
  //await micropip.install(`${HOST}/wheel/pytigon_lib-0.250419-py3-none-any.whl`)
  await micropip.install('cryptography')
  await micropip.install('requests')
  await micropip.install('six')
  await micropip.install('py-vapid')
  await micropip.install('webtest')
  await micropip.install('pywebpush')
  await micropip.install('django-pwa-webpush')
  await micropip.install('bcrypt')
  await micropip.install('pytigon')
  //await micropip.install(`${HOST}/wheel/pytigon-0.250419-py3-none-any.whl`)
}

function syncfs (populate) {
  return new Promise(resolve => {
    PYODIDE.FS.syncfs(populate, response => resolve(response))
  })
}

const setup_python = async () => {
  console.log('SETUP 1:')
  if (PYODIDE == null) {
    PYODIDE = await loadPyodide()
    console.log('SETUP 2:')
    let mountDir = '/home/pyodide/pytigon_data'
    PYODIDE.FS.mkdirTree(mountDir)
    PYODIDE.FS.mount(PYODIDE.FS.filesystems.IDBFS, {}, mountDir)
    console.log('SETUP 3:')
    let mountDir2 = '/lib/python3.12/site-packages'
    PYODIDE.FS.mkdirTree(mountDir2)
    PYODIDE.FS.mount(PYODIDE.FS.filesystems.IDBFS, {}, mountDir2)
    console.log('SETUP 4:')
    await syncfs(true)
    console.log('SETUP 5:')
  }
  const need_for_installation = await PYODIDE.runPythonAsync(`
    try:
      import django
      ret = False
    except:
      ret = True
    ret
  `)
  console.log('SETUP 6:')

  if (need_for_installation) {
    await installPython()
    PYODIDE.FS.syncfs(false, callback_func)
  }
  console.log('SETUP 7:')

  LOADED = 2

  var create_auto_user = 'False'
  if (need_for_installation) {
    create_auto_user = 'True'
  }
  console.log('SETUP 8:')

  txt = PYTIGON_INIT.replaceAll('{{PRJ_NAME}}', PRJ_NAME)
    .replaceAll('{{USER}}', 'auto')
    .replaceAll('{{PASSWORD}}', 'anawa')
    .replaceAll('{{HOST}}', HOST)
    .replaceAll('{{CREATE_AUTO_USER}}', create_auto_user)
  await PYODIDE.runPythonAsync(txt)
  console.log('SETUP 9:')
  if (LOCK != null) {
    LOCK.disable()
  }
}

self.addEventListener('install', event => {
  LOADED = 1
  LOCK = new AsyncLock()
  LOCK.enable()
  event.waitUntil(setup_python())
})

const django_request = async request => {
  response = await caches.match(request.url)
  if (response !== undefined) {
    console.log('IN CACHE: :' + request.url)
    return response
  }

  if (
    request.url == HOST + '/' ||
    request.url == HOST + '/app.js' ||
    request.url == HOST + '/manifest.json'
  ) {
    let net_response = await fetch(request)
    const responseClone = net_response.clone()
    caches.open('v1').then(cache => {
      cache.put(request.url, responseClone)
    })
    console.log('GET: :' + request.url)
    return net_response
  }

  if (LOADED == 1) {
    console.log('WAIT: ' + request.url)
    await LOCK.promise
    console.log('WAIT END: ' + request.url)
  }

  let cookie = ''
  for (const key in COOKIES) {
    const val = `${key}=${COOKIES[key]}`
    cookie += cookie ? `; ${val}` : val
  }

  var url
  if (request.url == HOST + '/') {
    url = request.url.replaceAll(HOST, `http://127.0.0.2/${PRJ_NAME}`)
  } else {
    url = request.url.replaceAll(HOST, `http://127.0.0.2`)
  }
  const method = request.method.toLowerCase()
  let params = ''
  if (['post', 'put', 'patch'].includes(method)) {
    params = await request.text()
  }

  const url_search_params = new URLSearchParams(params)
  const params2 = Object.fromEntries(url_search_params.entries())

  params3 = JSON.stringify(params2)

  const py_data = PYODIDE.runPython(`
    params4 = json.loads('${params3}')
    if params4:
      response = request2('${url}', params4)
    else:
      response = request2('${url}')
    if response.ret_content_type.startswith('text'):
      x = response.str()
    else:
      x = response.ptr()
    [json.dumps(response.response.headers if hasattr(response.response, 'headers') else {}), json.dumps(response.response.cookies if hasattr(response.response, 'cookies') else {}), json.dumps(response.ret_content_type), x]
  `)

  if (params != '') {
    PYODIDE.FS.syncfs(false, callback_func)
  }

  const resp_headers = JSON.parse(py_data[0])
  const resp_cookies = JSON.parse(py_data[1])
  const resp_content_type = JSON.parse(py_data[2])
  var response = py_data[3]

  if (resp_cookies) {
    for (const key in resp_cookies) {
      COOKIES[key] = resp_cookies[key]
    }
  }

  if (typeof response === 'string' || response instanceof String) {
  } else {
    if (resp_content_type === 'application/octet-stream') {
      if (request.url.includes('.woff2')) {
        resp_headers['Content-Type'] = 'font/woff2'
      } else if (request.url.includes('.woff')) {
        resp_headers['Content-Type'] = 'font/woff'
      } else if (request.url.includes('.ttf')) {
        resp_headers['Content-Type'] = 'font/ttf'
      }
    }
    response = response.toJs()
  }

  const status = PYODIDE.runPython(
    'response.response.status_code if hasattr(response.response, "status_code") else 200'
  )
  if (status === 302 || status === 301) {
    return Response.redirect(resp_headers['Location'], status)
  }

  let pytigon_response = new Response(response, {
    headers: resp_headers,
    status: status
  })

  let ret_response = new Response(response, {
    headers: resp_headers,
    status: status
  })

  if (resp_headers['cache-control'] !== undefined) {
    caches.open('v1').then(cache => {
      cache.put(request.url, pytigon_response)
      console.log('PUT :' + request.url)
    })
  }

  return ret_response
}

self.addEventListener('fetch', event => {
  if (LOADED == 0) {
    console.log('LOCK MASTER 1:')
    LOADED = 1
    LOCK = new AsyncLock()
    LOCK.enable()
    console.log('LOCK MASTER 2:')
    event.waitUntil(setup_python())
    console.log('LOCK MASTER 3:')
  }
  event.respondWith(django_request(event.request))
})

self.addEventListener('activate', function (event) {
  event.waitUntil(self.clients.claim())
})

function init_callback () {
  h = document.getElementsByTagName('HTML')[0]
  b = h.querySelector('body')
  while (b.firstChild) {
    b.removeChild(b.lastChild)
  }
  m = h.lastChild

  while (m.firstChild) {
    b.appendChild(m.firstChild)
  }
  h.removeChild(h.lastChild)
}

window.init_callback = init_callback

async function replacePageContent (url) {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const html = await response.text()

    let h = document.getElementsByTagName('HTML')[0]
    let doc = new DOMParser().parseFromString(html, 'text/html')

    div = document.createElement('div')
    div.style.display = 'none'
    div.innerHTML = doc.body.innerHTML

    h.appendChild(div)
    head = h.querySelector('head')

    head.innerHTML = head.innerHTML + doc.head.innerHTML

    div2 = document.createElement('div')
    div2.innerHTML = html

    const scripts = div2.querySelectorAll('script')

    scripts.forEach(script => script.remove())

    for (const script of scripts) {
      try {
        const newScript = document.createElement('script')

        Array.from(script.attributes).forEach(attr => {
          newScript.setAttribute(attr.name, attr.value)
        })

        if (script.src) {
          await new Promise((resolve, reject) => {
            newScript.onload = resolve
            newScript.onerror = reject
            document.head.appendChild(newScript)
          })
        } else {
          newScript.textContent = script.textContent
          document.head.appendChild(newScript)
        }

        console.log('Script executed:', script.src || 'inline script')
      } catch (e) {
        console.error('Error executing script:', e)
      }
    }

    window.history.pushState({}, '', url)
  } catch (error) {
    console.error('Error fetching the URL:', error)
  }
}

if ('serviceWorker' in navigator) {
  navigator.serviceWorker
    .register(
      './worker.js?PRJ_NAME=' +
        window.PYTIGON_PRJ_NAME +
        '&HOST=' +
        window.location.origin
    )
    .then(
      registration => {
        console.log('Service worker registration succeeded:', registration)
        if (
          registration.active != null &&
          registration.active.state === 'activated'
        ) {
          replacePageContent('/' + window.PYTIGON_PRJ_NAME + '/')
        } else {
          registration.installing?.addEventListener('statechange', event => {
            if (event.target.state === 'activated') {
              replacePageContent('/' + window.PYTIGON_PRJ_NAME + '/')
            }
          })
          registration.waiting?.addEventListener('statechange', event => {
            if (event.target.state === 'activated') {
              replacePageContent('/' + window.PYTIGON_PRJ_NAME + '/')
            }
          })
          registration.active?.addEventListener('statechange', event => {
            replacePageContent('/' + window.PYTIGON_PRJ_NAME + '/')
          })
        }
      },
      error => {
        alert(`Service worker registration failed: ${error}`)
      }
    )
} else {
  alert('Service workers are not supported in this browser.')
}

var CACHE_PREFIX = 'twweb-cache'
var CACHE_VERSION = '1'
var CACHE_NAME = CACHE_PREFIX + '-v' + CACHE_VERSION
var shellFiles = [
    '/offline',
    '/style.css',
    '/icon-512.png',
    '/sw-register.js',
    '/manifest.json',

    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js',
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.3/css/bootstrap.min.css',
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.3/js/bootstrap.min.js',
    'https://use.fontawesome.com/releases/v5.0.12/css/all.css',
]

self.addEventListener('install', function(event) {
    console.log('[TWWeb] Installing')

    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            console.debug('[TWWeb] Caching TWWeb shell...');
            return cache.addAll(shellFiles);
        })
    )
});

self.addEventListener('activate', function(event) {
    console.log('[TWWeb] Activating new Service Worker')

    const clearCache = async () => {
        names = await caches.keys(CACHE_NAME)
        names.filter(function(cname) {
            return cname != CACHE_NAME && cname.startsWith(CACHE_PREFIX);
        }).map(function(cname) {
            console.debug('[TWweb] Removing stale cache: ', cname);
            return caches.delete(cname);
        });
    }
    event.waitUntil(clearCache());
});

self.addEventListener('fetch', function(event) {
    const fallback = async (show_offline=true, no_use_status='disconnected') => {
        if (show_offline) {
            var cache = await caches.open(CACHE_NAME);
            return cache.match('/offline') || Promise.reject('missing-offline');
        }
        return Promise.reject(no_use_status)
    }

    const networkWithCacheUpdate = async (request, show_offline=false) => {
        let reqClone = request.clone();
        var cache = await caches.open(CACHE_NAME);

        try {
            var response = await fetch(request);
            await cache.put(reqClone, response.clone());
            return response;
        }
        catch (err) {
            console.error(err);

            var m = await cache.match(reqClone);
            if (m) {
                console.debug('[TWWeb] Serving from cache: ', request.url)
                return m;
            }

            return await fallback(show_offline);
        }
    }

    const cacheOrFetch = async (request, show_offline=false) => {
        var cache = await caches.open(CACHE_NAME);
        var response = await cache.match(request.clone());

        if (response) {
            console.debug('[TWWeb] Serving from cache: ', request.url)
            return response;
        }

        try {
            return await fetch(request);
        }
        catch (ferr) {
            return await fallback(show_offline);
        }
    }

    const cacheOrFetchUpdate = async (request, show_offline=false, bg_cache=false) => {
        var cache = await caches.open(CACHE_NAME);
        var response = await cache.match(request.clone());

        if (response) {
            console.debug('[TWWeb] Serving from cache: ', request.url);
            if (bg_cache) {
                event.waitUntil(backgroundCache(request));
            }
            return response;
        }

        try {
            var newResponse = await fetch(request.clone());
            if (newResponse.ok) {
                cache.put(request, newResponse.clone());
            }
            return newResponse;
        }
        catch (err) {
            console.error(err);
            console.error('[TWWeb] No content for: ', request.url);
            return await fallback(show_offline);
        }
    }

    const backgroundCache = async (request) => {
        var cache = await caches.open(CACHE_NAME);
        try {
            console.debug('[TWWeb] Initialized Background cache update for ',
                request.url)
            var response = await fetch(request.clone());
            if (response.ok) {
                console.debug('[TWWeb] Background update OK: ', request.url)
                cache.put(request, response.clone());
            }
            else {
                console.error('[TWWeb] Background update failed: ', 
                    request.url, ', code: ', response.status)
            }
            return response;
        }
        catch (err) {
            console.error(err);
            return Promise.reject('no-connection');
        }
    }

    //
    // Logic starts here
    //////////////////////////

    if (event.request.method != 'GET') {
        return;
    }

    url = new URL(event.request.url);

    // non-local urls won't get any love from us.
    if (url.origin != location.origin) {
        event.respondWith(cacheOrFetch(event.request));
        return;
    }

    // static assets - won't be updated if they're already in cache
    if (/\.(css|js|json|png)$/.test(url.pathname)) {
        event.respondWith(cacheOrFetchUpdate(event.request));
        return;
    }

    // non-static, but never changing assets
    if (/\/(offline)$/.test(url.pathname)) {
        event.respondWith(cacheOrFetchUpdate(event.request));
        return;
    }

    // things that will probably break without network (CSRF)...
    if (url.pathname == '/' || /\/(add$|edit\/|login$)/.test(url.pathname)) {
        event.respondWith(networkWithCacheUpdate(event.request, true));
        return;
    }

    // default behaviour
    event.respondWith(networkWithCacheUpdate(event.request, true));
});

if('serviceWorker' in navigator) {
    if (!navigator.serviceWorker.controller) {
        navigator.serviceWorker.register('sw.js', {
            scope: './'
        }).then(function(reg) {
            console.log('[TWWeb] Service worker has been registered for scope:'+ reg.scope);
        });
    }
}

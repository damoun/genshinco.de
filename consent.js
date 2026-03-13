(function () {
  var GA_ID = 'G-D7SJ1CFN3S';
  var ADSENSE_PUB = 'ca-pub-1179795888748652';
  var STORAGE_KEY = 'cookie_consent';

  // --- Consent Mode v2: set defaults BEFORE gtag loads ---
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    wait_for_update: 500
  });
  gtag('js', new Date());
  gtag('config', GA_ID);

  function loadGA() {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
  }

  function loadAdSense() {
    var s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + ADSENSE_PUB;
    document.head.appendChild(s);
  }

  function grantConsent() {
    gtag('consent', 'update', {
      ad_storage: 'granted',
      ad_user_data: 'granted',
      ad_personalization: 'granted',
      analytics_storage: 'granted'
    });
    loadGA();
    loadAdSense();
  }

  function hideBanner() {
    var banner = document.getElementById('cookie-banner');
    if (banner) banner.remove();
  }

  function onAccept() {
    localStorage.setItem(STORAGE_KEY, 'granted');
    grantConsent();
    hideBanner();
  }

  function onReject() {
    localStorage.setItem(STORAGE_KEY, 'denied');
    hideBanner();
  }

  function showBanner() {
    var banner = document.createElement('div');
    banner.id = 'cookie-banner';
    banner.innerHTML =
      '<div style="' +
        'position:fixed;bottom:0;left:0;right:0;z-index:9999;' +
        'background:#252A3D;border-top:1px solid rgba(78,205,196,0.2);' +
        'color:#A1BECAFF;font-family:inherit;font-size:14px;' +
        'display:flex;align-items:center;justify-content:space-between;' +
        'flex-wrap:wrap;gap:12px;padding:14px 20px;' +
      '">' +
        '<span>This site uses cookies for analytics and ads. ' +
          '<a href="/privacy.html" style="color:#4ECDC4;text-decoration:underline;">Privacy Policy</a>' +
        '</span>' +
        '<span style="display:flex;gap:10px;">' +
          '<button id="consent-reject" style="' +
            'background:transparent;border:1px solid rgba(78,205,196,0.4);' +
            'color:#A1BECAFF;padding:7px 18px;border-radius:6px;cursor:pointer;font-size:13px;' +
          '">Reject</button>' +
          '<button id="consent-accept" style="' +
            'background:#4ECDC4;border:none;' +
            'color:#1C1F2E;padding:7px 18px;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;' +
          '">Accept</button>' +
        '</span>' +
      '</div>';
    document.body.appendChild(banner);
    document.getElementById('consent-accept').addEventListener('click', onAccept);
    document.getElementById('consent-reject').addEventListener('click', onReject);
  }

  var stored = localStorage.getItem(STORAGE_KEY);
  if (stored === 'granted') {
    grantConsent();
  } else if (!stored) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }
  // If stored === 'denied', do nothing - consent stays denied, no banner shown.
})();

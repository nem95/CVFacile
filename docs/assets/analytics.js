// SPDX-License-Identifier: AGPL-3.0-or-later
// PostHog analytics with a cookie banner: cookieless until the visitor accepts cookies.
// The token comes from <meta name="posthog-key">, filled by scripts/build_site.py (POSTHOG_KEY).

(function () {
  var CONSENT_KEY = "cvf_consent";

  function meta(name) {
    var el = document.querySelector('meta[name="' + name + '"]');
    var value = el ? el.content : "";
    return value && value.indexOf("__") !== 0 ? value : "";
  }

  function readChoice() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (_) { return null; }
  }

  function saveChoice(value) {
    try { localStorage.setItem(CONSENT_KEY, value); } catch (_) { /* private mode: ask again next time */ }
  }

  var key = meta("posthog-key");
  var host = meta("posthog-host") || "https://eu.i.posthog.com";
  window.cvfTrack = function () {};
  if (!key) return;

  // Official PostHog loader snippet (https://posthog.com/docs/web-analytics/installation/web).
  !function(t,e){var o,n,p,r;e.__SV||(window.posthog && window.posthog.__loaded)||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}p||((p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",p.onerror=function(){p=null},(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r));var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],Object.defineProperty(u,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}}),Object.defineProperty(u.people,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(){return u.toString(1)+".people (stub)"}}),o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagResult isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);

  var choice = readChoice();
  var config = {
    api_host: host,
    defaults: "2026-08-30",
    person_profiles: "identified_only",
    capture_exceptions: true,
  };
  if (choice !== "granted") config.cookieless_mode = "always";
  window.posthog.init(key, config);
  window.posthog.register({ site_lang: document.documentElement.lang, consent: choice || "pending" });

  window.cvfTrack = function (event, properties) {
    window.posthog.capture(event, properties || {});
  };

  // Consent banner: shown until the visitor chooses.
  var banner = document.getElementById("consent");
  if (!banner || choice) return;
  banner.hidden = false;
  banner.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-consent]");
    if (!btn) return;
    var value = btn.getAttribute("data-consent");
    saveChoice(value);
    window.cvfTrack("cookie_consent_chosen", { choice: value });
    banner.hidden = true;
  });
})();

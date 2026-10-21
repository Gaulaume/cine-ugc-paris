package fr.cine.paris;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * Affiche le site Ciné en plein écran. Les liens extérieurs (réservation, Letterboxd, Google Maps,
 * agenda) s'ouvrent dans leur propre appli ; « Partager » ouvre le menu de partage d'Android.
 */
public class MainActivity extends Activity {
    static final String HOME = "https://gaulaume.github.io/cine-ugc-paris/";
    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        web = new WebView(this);
        setContentView(web);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);   // envies, déjà vus, réglages
        s.setDatabaseEnabled(true);
        s.setUserAgentString(s.getUserAgentString() + " CineAndroid/1");
        web.addJavascriptInterface(new Bridge(), "CineApp");
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                return openOutside(req.getUrl());
            }
        });
        if (state != null) web.restoreState(state);
        else web.loadUrl(HOME);
    }

    /** true = lien géré hors de l'appli (autre appli ou navigateur). */
    private boolean openOutside(Uri uri) {
        String url = uri.toString();
        if (url.startsWith(HOME)) return false;
        try {
            if (url.startsWith("intent:")) {   // ex. Letterboxd : ouvre l'appli, sinon le site de repli
                Intent i = Intent.parseUri(url, Intent.URI_INTENT_SCHEME);
                try { startActivity(i); }
                catch (ActivityNotFoundException e) {
                    String fallback = i.getStringExtra("browser_fallback_url");
                    if (fallback != null) startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(fallback)));
                }
            } else {
                startActivity(new Intent(Intent.ACTION_VIEW, uri));
            }
        } catch (Exception ignored) { }
        return true;
    }

    /** Fonctions appelables depuis la page : window.CineApp.share(texte). */
    class Bridge {
        @JavascriptInterface
        public void share(String text) {
            runOnUiThread(() -> {
                Intent i = new Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_TEXT, text);
                startActivity(Intent.createChooser(i, "Partager la séance"));
            });
        }
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }
}

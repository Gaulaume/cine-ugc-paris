package fr.cine.paris;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

/**
 * Page de réservation (ugc.fr, mk2.com, billetteries des indépendants) ouverte dans Ciné, sous
 * une barre aux couleurs de l'appli : on ne passe plus par l'appli UGC ni par le navigateur.
 * La connexion aux sites est gardée d'une fois sur l'autre (cookies). « Garder le billet »
 * enregistre ce qui est à l'écran (QR code de la confirmation) dans « Mes billets ».
 */
public class BookingActivity extends Activity {
    static final String EXTRA_TITLE = "title", EXTRA_SUB = "sub";
    static final int BG = 0xFF0B0F1A, INK = 0xFFEEF1F7, MUTED = 0xFF8E97AD, TICKET = 0xFFF2C230, TICKET_INK = 0xFF1B2A4E;

    private WebView web;
    private ProgressBar progress;
    private TextView titleView, hostView;
    private View errorView;
    private String title, sub;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        overridePendingTransition(R.anim.slide_up, R.anim.stay);
        title = getIntent().getStringExtra(EXTRA_TITLE);
        sub = getIntent().getStringExtra(EXTRA_SUB);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(BG);
        root.addView(toolbar(), new LinearLayout.LayoutParams(-1, dp(58)));

        progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progress.setMax(100);
        progress.setProgressTintList(android.content.res.ColorStateList.valueOf(TICKET));
        progress.setProgressBackgroundTintList(android.content.res.ColorStateList.valueOf(BG));
        root.addView(progress, new LinearLayout.LayoutParams(-1, dp(3)));

        FrameLayout content = new FrameLayout(this);
        web = new WebView(this);
        web.setBackgroundColor(Color.WHITE);
        content.addView(web, new FrameLayout.LayoutParams(-1, -1));
        errorView = errorView();
        content.addView(errorView, new FrameLayout.LayoutParams(-1, -1));
        root.addView(content, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(root);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setSupportMultipleWindows(false);   // les target="_blank" restent dans cette page
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(web, true);   // paiement, 3-D Secure

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                return handleSpecial(req.getUrl());
            }
            @Override
            public void onPageStarted(WebView view, String url, Bitmap icon) {
                errorView.setVisibility(View.GONE);
                showHost(url);
            }
            @Override
            public void onPageFinished(WebView view, String url) {
                showHost(url);
                CookieManager.getInstance().flush();
            }
            @Override
            public void onReceivedError(WebView view, WebResourceRequest req, WebResourceError err) {
                if (req.isForMainFrame()) errorView.setVisibility(View.VISIBLE);
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int p) {
                progress.setProgress(p);
                progress.setVisibility(p < 100 ? View.VISIBLE : View.INVISIBLE);
            }
            @Override
            public void onReceivedTitle(WebView view, String t) {
                if (TextUtils.isEmpty(title)) titleView.setText(t);
            }
        });
        // Billet en PDF, etc. : on laisse Android l'ouvrir.
        web.setDownloadListener((url, ua, cd, mime, len) -> openOutside(Uri.parse(url)));

        if (state != null) web.restoreState(state);
        else web.loadUrl(getIntent().getDataString());
    }

    /** Liens que la page web ne peut pas ouvrir elle-même : appli bancaire, téléphone, mail… */
    private boolean handleSpecial(Uri uri) {
        String scheme = uri.getScheme() == null ? "" : uri.getScheme();
        if (scheme.equals("http") || scheme.equals("https")) return false;   // tout reste ici
        if (scheme.equals("intent")) {
            try {
                Intent i = Intent.parseUri(uri.toString(), Intent.URI_INTENT_SCHEME);
                String pkg = i.getPackage() == null ? "" : i.getPackage();
                String fallback = i.getStringExtra("browser_fallback_url");
                // Les sites essaient parfois d'ouvrir leur propre appli (UGC…) : on reste sur le site.
                if (pkg.contains("ugc") || pkg.contains("mk2")) {
                    if (fallback != null) web.loadUrl(fallback);
                    return true;
                }
                i.addCategory(Intent.CATEGORY_BROWSABLE).setComponent(null).setSelector(null);
                startActivity(i);
            } catch (Exception e) { /* rien à ouvrir */ }
            return true;
        }
        openOutside(uri);
        return true;
    }

    private void openOutside(Uri uri) {
        try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); } catch (Exception ignored) { }
    }

    private void showHost(String url) {
        String host = Uri.parse(url).getHost();
        if (host == null) return;
        host = host.replaceFirst("^www\\.", "");
        boolean secure = url.startsWith("https:");
        String line = (secure ? "🔒 " : "") + host;
        hostView.setText(TextUtils.isEmpty(sub) ? line : sub + "  ·  " + line);
    }

    /** Enregistre la page affichée (QR code du billet) dans « Mes billets ». */
    private void keepTicket() {
        if (web.getWidth() == 0) return;
        Bitmap bmp = Bitmap.createBitmap(web.getWidth(), web.getHeight(), Bitmap.Config.ARGB_8888);
        web.draw(new Canvas(bmp));
        String name = TextUtils.isEmpty(title) ? web.getTitle() : title;
        boolean ok = Tickets.save(this, bmp, name, sub, web.getUrl());
        Toast.makeText(this, ok ? "Billet gardé dans Ciné (🎟 en haut de l'appli)" : "Impossible d'enregistrer le billet", Toast.LENGTH_LONG).show();
    }

    // --- Interface ---

    private View toolbar() {
        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setBackgroundColor(BG);
        bar.setPadding(dp(4), 0, dp(10), 0);

        TextView close = new TextView(this);
        close.setText("✕");
        close.setTextColor(INK);
        close.setTextSize(20);
        close.setGravity(Gravity.CENTER);
        close.setContentDescription("Revenir à Ciné");
        close.setOnClickListener(v -> finish());
        bar.addView(close, new LinearLayout.LayoutParams(dp(48), dp(48)));

        LinearLayout texts = new LinearLayout(this);
        texts.setOrientation(LinearLayout.VERTICAL);
        titleView = new TextView(this);
        titleView.setTextColor(INK);
        titleView.setTextSize(16);
        titleView.setTypeface(Typeface.create("sans-serif-condensed", Typeface.BOLD));
        titleView.setSingleLine(true);
        titleView.setEllipsize(TextUtils.TruncateAt.END);
        titleView.setText(TextUtils.isEmpty(title) ? "Réservation" : title);
        hostView = new TextView(this);
        hostView.setTextColor(MUTED);
        hostView.setTextSize(12);
        hostView.setSingleLine(true);
        hostView.setEllipsize(TextUtils.TruncateAt.END);
        if (!TextUtils.isEmpty(sub)) hostView.setText(sub);
        texts.addView(titleView);
        texts.addView(hostView);
        bar.addView(texts, new LinearLayout.LayoutParams(0, -2, 1));

        TextView keep = new TextView(this);
        keep.setText("🎟 Garder le billet");
        keep.setTextColor(TICKET_INK);
        keep.setTextSize(13);
        keep.setTypeface(Typeface.DEFAULT_BOLD);
        keep.setGravity(Gravity.CENTER);
        keep.setPadding(dp(10), 0, dp(10), 0);
        GradientDrawable pill = new GradientDrawable();
        pill.setColor(TICKET);
        pill.setCornerRadius(dp(8));
        keep.setBackground(pill);
        keep.setContentDescription("Garder le billet affiché dans Ciné");
        keep.setOnClickListener(v -> keepTicket());
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-2, dp(34));
        lp.leftMargin = dp(8);
        bar.addView(keep, lp);
        return bar;
    }

    private View errorView() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setGravity(Gravity.CENTER);
        box.setBackgroundColor(BG);
        box.setPadding(dp(32), 0, dp(32), 0);
        box.setVisibility(View.GONE);
        TextView h = new TextView(this);
        h.setText("Page indisponible");
        h.setTextColor(INK);
        h.setTextSize(20);
        h.setTypeface(Typeface.DEFAULT_BOLD);
        h.setGravity(Gravity.CENTER);
        TextView p = new TextView(this);
        p.setText("Vérifie ta connexion, puis réessaie.");
        p.setTextColor(MUTED);
        p.setGravity(Gravity.CENTER);
        p.setPadding(0, dp(6), 0, dp(18));
        TextView retry = new TextView(this);
        retry.setText("Réessayer");
        retry.setTextColor(TICKET_INK);
        retry.setTypeface(Typeface.DEFAULT_BOLD);
        retry.setPadding(dp(22), dp(10), dp(22), dp(10));
        GradientDrawable pill = new GradientDrawable();
        pill.setColor(TICKET);
        pill.setCornerRadius(dp(10));
        retry.setBackground(pill);
        retry.setOnClickListener(v -> { errorView.setVisibility(View.GONE); web.reload(); });
        box.addView(h);
        box.addView(p);
        box.addView(retry, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return box;
    }

    private int dp(int v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, getResources().getDisplayMetrics());
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else finish();
    }

    @Override
    public void finish() {
        super.finish();
        overridePendingTransition(R.anim.stay, R.anim.slide_down);
    }

    @Override
    protected void onPause() {
        super.onPause();
        CookieManager.getInstance().flush();
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    protected void onDestroy() {
        web.destroy();
        super.onDestroy();
    }
}

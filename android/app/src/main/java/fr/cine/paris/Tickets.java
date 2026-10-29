package fr.cine.paris;

import android.content.Context;
import android.graphics.Bitmap;
import android.util.Base64;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.io.FileInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.Arrays;

/** « Mes billets » : captures des pages de confirmation, rangées dans la mémoire de l'appli. */
final class Tickets {
    private static final int MAX = 20;

    private static File dir(Context c) {
        File d = new File(c.getFilesDir(), "billets");
        d.mkdirs();
        return d;
    }

    static boolean save(Context c, Bitmap bmp, String title, String sub, String url) {
        String id = String.valueOf(System.currentTimeMillis());
        try (FileOutputStream img = new FileOutputStream(new File(dir(c), id + ".jpg"))) {
            bmp.compress(Bitmap.CompressFormat.JPEG, 85, img);
            JSONObject meta = new JSONObject()
                .put("id", id).put("title", title == null ? "" : title)
                .put("sub", sub == null ? "" : sub).put("url", url == null ? "" : url);
            try (FileOutputStream out = new FileOutputStream(new File(dir(c), id + ".json"))) {
                out.write(meta.toString().getBytes(StandardCharsets.UTF_8));
            }
            prune(c);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /** Liste JSON, du plus récent au plus ancien, images en data: URL. */
    static String list(Context c) {
        JSONArray out = new JSONArray();
        for (File meta : sorted(c)) {
            try {
                JSONObject o = new JSONObject(new String(read(meta), StandardCharsets.UTF_8));
                File img = new File(dir(c), o.getString("id") + ".jpg");
                if (!img.exists()) continue;
                o.put("img", "data:image/jpeg;base64," + Base64.encodeToString(read(img), Base64.NO_WRAP));
                out.put(o);
            } catch (Exception ignored) { }
        }
        return out.toString();
    }

    private static byte[] read(File f) throws java.io.IOException {
        try (InputStream in = new FileInputStream(f)) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[16384];
            for (int n; (n = in.read(buf)) > 0; ) out.write(buf, 0, n);
            return out.toByteArray();
        }
    }

    static void delete(Context c, String id) {
        if (!id.matches("\\d+")) return;
        new File(dir(c), id + ".jpg").delete();
        new File(dir(c), id + ".json").delete();
    }

    private static File[] sorted(Context c) {
        File[] metas = dir(c).listFiles((d, n) -> n.endsWith(".json"));
        if (metas == null) return new File[0];
        Arrays.sort(metas, (a, b) -> b.getName().compareTo(a.getName()));
        return metas;
    }

    private static void prune(Context c) {
        File[] metas = sorted(c);
        for (int i = MAX; i < metas.length; i++) delete(c, metas[i].getName().replace(".json", ""));
    }

    private Tickets() { }
}

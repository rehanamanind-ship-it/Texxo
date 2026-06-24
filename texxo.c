#include <gtk/gtk.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* ----- Color Map (name -> hex) ----- */
typedef struct {
    const char *name;
    const char *hex;
} ColorEntry;

static const ColorEntry color_map[] = {
    {"blue", "#61afef"}, {"red", "#ff6c6b"}, {"green", "#98c379"},
    {"yellow", "#e5c07b"}, {"orange", "#d19a66"}, {"purple", "#c678dd"},
    {"pink", "#ff79c6"}, {"cyan", "#56b6c2"}, {"white", "#abb2bf"},
    {"gray", "#5c6370"}, {"black", "#282c34"}, {"lime", "#7ec699"},
    {"teal", "#2aa198"}, {"coral", "#ff7f50"}, {"crimson", "#dc143c"},
    {"gold", "#ffd700"}, {"indigo", "#4b0082"}, {"lavender", "#e6e6fa"},
    {"magenta", "#ff00ff"}, {"maroon", "#800000"}, {"navy", "#000080"},
    {"olive", "#808000"}, {"plum", "#dda0dd"}, {"salmon", "#fa8072"},
    {"sienna", "#a0522d"}, {"tan", "#d2b48c"}, {"tomato", "#ff6347"},
    {"turquoise", "#40e0d0"}, {"violet", "#ee82ee"},
    {"md-red","#f44336"}, {"md-pink","#e91e63"}, {"md-purple","#9c27b0"},
    {"md-deep-purple","#673ab7"}, {"md-indigo","#3f51b5"}, {"md-blue","#2196f3"},
    {"md-light-blue","#03a9f4"}, {"md-cyan","#00bcd4"}, {"md-teal","#009688"},
    {"md-green","#4caf50"}, {"md-light-green","#8bc34a"}, {"md-lime","#cddc39"},
    {"md-yellow","#ffeb3b"}, {"md-amber","#ffc107"}, {"md-orange","#ff9800"},
    {"md-deep-orange","#ff5722"}, {"md-brown","#795548"}, {"md-grey","#9e9e9e"},
    {"md-blue-grey","#607d8b"},
    {"pastel-pink","#ffd1dc"}, {"pastel-blue","#aec6cf"}, {"pastel-green","#77dd77"},
    {"pastel-yellow","#fdfd96"}, {"pastel-purple","#b39eb5"}, {"pastel-orange","#ffb347"},
    {"pastel-mint","#98fb98"}, {"pastel-lavender","#e6e6fa"},
    {"neon-pink","#ff6ec7"}, {"neon-blue","#4d4dff"}, {"neon-green","#39ff14"},
    {"neon-yellow","#ffff00"}, {"neon-orange","#ff6600"}, {"neon-purple","#9d00ff"},
    {"neon-cyan","#00ffff"},
    {NULL, NULL}
};

/* Font list (name, size) */
typedef struct {
    const char *name;
    int size;
} FontEntry;

static const FontEntry font_map[] = {
    {"mono", 14}, {"clean", 14}, {"code", 14}, {"retro", 16},
    {"times", 14}, {"arial", 14}, {"helvetica", 14}, {"georgia", 14},
    {"verdana", 14}, {"trebuchet", 14}, {"comic", 14}, {"impact", 16},
    {"palatino", 14}, {"garamond", 14}, {"roboto", 14}, {"opensans", 14},
    {"lato", 14}, {"montserrat", 14}, {"poppins", 14}, {"raleway", 14},
    {"ubuntu", 14}, {"fira", 14}, {"jetbrains", 14}, {"source", 14},
    {"script", 18}, {"gothic", 14}, {"copper", 14}, {"papyrus", 16},
    {NULL, 0}
};

/* ----- Application Data Structure ----- */
typedef struct {
    GtkWidget *window;
    GtkWidget *main_vbox;
    GtkWidget *cmd_entry;
    GtkWidget *status_label;
    GtkWidget *status_bar;
    GtkWidget *line_numbers_view;
    GtkWidget *text_view;
    GtkTextBuffer *text_buffer;
    GtkWidget *scrolled_window;
    PangoFontDescription *default_font;
    int image_counter;
    GHashTable *bookmarks;
    char *current_file;
    int theme;   // 0=dark, 1=light
    char *last_search;
} TexxoEditor;

/* ----- Utility Functions ----- */
static GdkRGBA hex_to_rgba(const char *hex) {
    GdkRGBA color;
    gdk_rgba_parse(&color, hex);
    return color;
}

static const char* lookup_color(const char *name) {
    for (int i = 0; color_map[i].name; i++) {
        if (strcasecmp(name, color_map[i].name) == 0)
            return color_map[i].hex;
    }
    if (name[0] == '#') return name;
    return "#61afef"; /* default blue */
}

static void update_line_numbers(TexxoEditor *app) {
    int line_count = gtk_text_buffer_get_line_count(app->text_buffer);
    GString *numbers = g_string_new("");
    for (int i = 1; i <= line_count; i++) {
        g_string_append_printf(numbers, "%d\n", i);
    }
    GtkTextBuffer *buf = gtk_text_view_get_buffer(GTK_TEXT_VIEW(app->line_numbers_view));
    gtk_text_buffer_set_text(buf, numbers->str, -1);
    g_string_free(numbers, TRUE);
}

static void update_status(TexxoEditor *app, const char *msg, gboolean error) {
    char *markup = g_strdup_printf("<span foreground='%s'>%s</span>",
                                    error ? "#ff8787" : "#b7d2ff", msg);
    gtk_label_set_markup(GTK_LABEL(app->status_label), markup);
    g_free(markup);
}

static void update_status_bar(TexxoEditor *app) {
    GtkTextIter start_iter, end_iter;
    gtk_text_buffer_get_start_iter(app->text_buffer, &start_iter);
    gtk_text_buffer_get_end_iter(app->text_buffer, &end_iter);
    char *text = gtk_text_buffer_get_text(app->text_buffer, &start_iter, &end_iter, FALSE);

    int lines = gtk_text_buffer_get_line_count(app->text_buffer);
    int words = 0;
    char *tmp = g_strdup(text);
    char *token = strtok(tmp, " \t\n");
    while (token) { words++; token = strtok(NULL, " \t\n"); }
    g_free(tmp);

    GtkTextIter cursor;
    gtk_text_buffer_get_iter_at_mark(app->text_buffer, &cursor,
                                     gtk_text_buffer_get_insert(app->text_buffer));
    int line = gtk_text_iter_get_line(&cursor) + 1;
    int col = gtk_text_iter_get_line_offset(&cursor) + 1;

    char buf[256];
    snprintf(buf, sizeof(buf), "Lines: %d | Words: %d | Characters: %ld | Position: %d:%d",
             lines, words, strlen(text), line, col);
    gtk_label_set_text(GTK_LABEL(app->status_bar), buf);
    g_free(text);
}

/* ----- Formatting Functions ----- */
static void apply_bold(TexxoEditor *app) {
    GtkTextIter start, end;
    if (gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end)) {
        gtk_text_buffer_apply_tag_by_name(app->text_buffer, "bold", &start, &end);
        update_status(app, "Applied bold", FALSE);
    }
}

static void apply_italic(TexxoEditor *app) {
    GtkTextIter start, end;
    if (gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end)) {
        gtk_text_buffer_apply_tag_by_name(app->text_buffer, "italic", &start, &end);
        update_status(app, "Applied italic", FALSE);
    }
}

static void apply_underline(TexxoEditor *app) {
    GtkTextIter start, end;
    if (gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end)) {
        gtk_text_buffer_apply_tag_by_name(app->text_buffer, "underline", &start, &end);
        update_status(app, "Applied underline", FALSE);
    }
}

static void apply_strikethrough(TexxoEditor *app) {
    GtkTextIter start, end;
    if (gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end)) {
        gtk_text_buffer_apply_tag_by_name(app->text_buffer, "strikethrough", &start, &end);
        update_status(app, "Applied strikethrough", FALSE);
    }
}

static void apply_color(TexxoEditor *app, const char *color_name) {
    GtkTextIter start, end;
    if (!gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end))
        return;
    const char *hex = lookup_color(color_name);
    GdkRGBA rgba = hex_to_rgba(hex);
    char tag_name[64];
    snprintf(tag_name, sizeof(tag_name), "color_%s", hex);
    gtk_text_buffer_create_tag(app->text_buffer, tag_name,
                                "foreground-rgba", &rgba, NULL);
    gtk_text_buffer_apply_tag_by_name(app->text_buffer, tag_name, &start, &end);
    update_status(app, "Applied color", FALSE);
}

static void apply_highlight(TexxoEditor *app, const char *color_name) {
    GtkTextIter start, end;
    if (!gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end))
        return;
    const char *hex = lookup_color(color_name);
    GdkRGBA rgba = hex_to_rgba(hex);
    char tag_name[64];
    snprintf(tag_name, sizeof(tag_name), "highlight_%s", hex);
    gtk_text_buffer_create_tag(app->text_buffer, tag_name,
                                "background-rgba", &rgba,
                                "foreground", "black", NULL);
    gtk_text_buffer_apply_tag_by_name(app->text_buffer, tag_name, &start, &end);
    update_status(app, "Applied highlight", FALSE);
}

static void apply_font_family(TexxoEditor *app, const char *family) {
    GtkTextIter start, end;
    if (!gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end))
        return;
    PangoFontDescription *desc = pango_font_description_copy(app->default_font);
    pango_font_description_set_family(desc, family);
    char tag_name[64];
    snprintf(tag_name, sizeof(tag_name), "font_%s", family);
    gtk_text_buffer_create_tag(app->text_buffer, tag_name,
                                "font-desc", desc, NULL);
    gtk_text_buffer_apply_tag_by_name(app->text_buffer, tag_name, &start, &end);
    pango_font_description_free(desc);
    update_status(app, "Changed font family", FALSE);
}

static void apply_font_size(TexxoEditor *app, int size) {
    GtkTextIter start, end;
    if (!gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end))
        return;
    PangoFontDescription *desc = pango_font_description_copy(app->default_font);
    pango_font_description_set_size(desc, size * PANGO_SCALE);
    char tag_name[32];
    snprintf(tag_name, sizeof(tag_name), "fontsize_%d", size);
    gtk_text_buffer_create_tag(app->text_buffer, tag_name,
                                "font-desc", desc, NULL);
    gtk_text_buffer_apply_tag_by_name(app->text_buffer, tag_name, &start, &end);
    pango_font_description_free(desc);
    update_status(app, "Changed font size", FALSE);
}

static void apply_font_style(TexxoEditor *app, const char *style) {
    for (int i = 0; font_map[i].name; i++) {
        if (strcasecmp(style, font_map[i].name) == 0) {
            GtkTextIter start, end;
            if (!gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end))
                return;
            PangoFontDescription *desc = pango_font_description_new();
            pango_font_description_set_family(desc, font_map[i].name);
            pango_font_description_set_size(desc, font_map[i].size * PANGO_SCALE);
            char tag_name[64];
            snprintf(tag_name, sizeof(tag_name), "fontstyle_%s", style);
            gtk_text_buffer_create_tag(app->text_buffer, tag_name,
                                        "font-desc", desc, NULL);
            gtk_text_buffer_apply_tag_by_name(app->text_buffer, tag_name, &start, &end);
            pango_font_description_free(desc);
            update_status(app, "Applied font style", FALSE);
            return;
        }
    }
    update_status(app, "Unknown font style", TRUE);
}

static void apply_alignment(TexxoEditor *app, GtkJustification justify) {
    GtkTextIter start, end;
    if (!gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end))
        return;
    const char *tag;
    switch (justify) {
        case GTK_JUSTIFY_LEFT: tag = "align_left"; break;
        case GTK_JUSTIFY_CENTER: tag = "align_center"; break;
        case GTK_JUSTIFY_RIGHT: tag = "align_right"; break;
        default: return;
    }
    gtk_text_buffer_apply_tag_by_name(app->text_buffer, tag, &start, &end);
    update_status(app, "Applied alignment", FALSE);
}

static void indent_selection(TexxoEditor *app) {
    GtkTextIter start, end;
    if (!gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end))
        return;
    char *text = gtk_text_buffer_get_text(app->text_buffer, &start, &end, FALSE);
    char **lines = g_strsplit(text, "\n", -1);
    GString *result = g_string_new("");
    for (int i = 0; lines[i]; i++) {
        g_string_append(result, "    ");
        g_string_append(result, lines[i]);
        if (lines[i+1]) g_string_append_c(result, '\n');
    }
    gtk_text_buffer_delete(app->text_buffer, &start, &end);
    gtk_text_buffer_insert(app->text_buffer, &start, result->str, -1);
    g_string_free(result, TRUE);
    g_strfreev(lines);
    g_free(text);
    update_status(app, "Indented selection", FALSE);
}

static void outdent_selection(TexxoEditor *app) {
    GtkTextIter start, end;
    if (!gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end))
        return;
    char *text = gtk_text_buffer_get_text(app->text_buffer, &start, &end, FALSE);
    char **lines = g_strsplit(text, "\n", -1);
    GString *result = g_string_new("");
    for (int i = 0; lines[i]; i++) {
        const char *line = lines[i];
        if (strncmp(line, "    ", 4) == 0)
            line += 4;
        else if (line[0] == '\t')
            line++;
        g_string_append(result, line);
        if (lines[i+1]) g_string_append_c(result, '\n');
    }
    gtk_text_buffer_delete(app->text_buffer, &start, &end);
    gtk_text_buffer_insert(app->text_buffer, &start, result->str, -1);
    g_string_free(result, TRUE);
    g_strfreev(lines);
    g_free(text);
    update_status(app, "Outdented selection", FALSE);
}

static void clear_formatting(TexxoEditor *app) {
    GtkTextIter start, end;
    if (gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end)) {
        gtk_text_buffer_remove_all_tags(app->text_buffer, &start, &end);
        update_status(app, "Cleared formatting", FALSE);
    }
}

static void new_document(TexxoEditor *app) {
    gtk_text_buffer_set_text(app->text_buffer, "", -1);
    g_free(app->current_file);
    app->current_file = NULL;
    update_status(app, "New document", FALSE);
}

static void open_file(TexxoEditor *app, const char *filename) {
    if (!filename) {
        GtkWidget *dialog = gtk_file_chooser_dialog_new("Open File",
                                    GTK_WINDOW(app->window),
                                    GTK_FILE_CHOOSER_ACTION_OPEN,
                                    "_Cancel", GTK_RESPONSE_CANCEL,
                                    "_Open", GTK_RESPONSE_ACCEPT,
                                    NULL);
        if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
            char *path = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));
            gtk_widget_destroy(dialog);
            open_file(app, path);
            g_free(path);
            return;
        }
        gtk_widget_destroy(dialog);
        return;
    }
    char *contents;
    gsize len;
    if (g_file_get_contents(filename, &contents, &len, NULL)) {
        gtk_text_buffer_set_text(app->text_buffer, contents, len);
        g_free(contents);
        g_free(app->current_file);
        app->current_file = g_strdup(filename);
        update_status(app, "Opened file", FALSE);
    } else {
        update_status(app, "Failed to open file", TRUE);
    }
}

static void save_file(TexxoEditor *app, const char *filename) {
    if (!filename && app->current_file)
        filename = app->current_file;
    if (!filename) {
        GtkWidget *dialog = gtk_file_chooser_dialog_new("Save File",
                                    GTK_WINDOW(app->window),
                                    GTK_FILE_CHOOSER_ACTION_SAVE,
                                    "_Cancel", GTK_RESPONSE_CANCEL,
                                    "_Save", GTK_RESPONSE_ACCEPT,
                                    NULL);
        gtk_file_chooser_set_do_overwrite_confirmation(GTK_FILE_CHOOSER(dialog), TRUE);
        if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
            char *path = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));
            gtk_widget_destroy(dialog);
            save_file(app, path);
            g_free(path);
            return;
        }
        gtk_widget_destroy(dialog);
        return;
    }
    GtkTextIter start_iter, end_iter;
    gtk_text_buffer_get_start_iter(app->text_buffer, &start_iter);
    gtk_text_buffer_get_end_iter(app->text_buffer, &end_iter);
    char *text = gtk_text_buffer_get_text(app->text_buffer, &start_iter, &end_iter, FALSE);
    if (g_file_set_contents(filename, text, -1, NULL)) {
        g_free(app->current_file);
        app->current_file = g_strdup(filename);
        gtk_text_buffer_set_modified(app->text_buffer, FALSE);
        update_status(app, "Saved file", FALSE);
    } else {
        update_status(app, "Failed to save file", TRUE);
    }
    g_free(text);
}

static void insert_image(TexxoEditor *app, const char *path) {
    if (!path) {
        GtkWidget *dialog = gtk_file_chooser_dialog_new("Insert Image",
                                    GTK_WINDOW(app->window),
                                    GTK_FILE_CHOOSER_ACTION_OPEN,
                                    "_Cancel", GTK_RESPONSE_CANCEL,
                                    "_Insert", GTK_RESPONSE_ACCEPT,
                                    NULL);
        GtkFileFilter *filter = gtk_file_filter_new();
        gtk_file_filter_add_pixbuf_formats(filter);
        gtk_file_chooser_set_filter(GTK_FILE_CHOOSER(dialog), filter);
        if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
            char *filename = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));
            gtk_widget_destroy(dialog);
            insert_image(app, filename);
            g_free(filename);
            return;
        }
        gtk_widget_destroy(dialog);
        return;
    }
    GError *error = NULL;
    GdkPixbuf *pixbuf = gdk_pixbuf_new_from_file(path, &error);
    if (error) {
        update_status(app, error->message, TRUE);
        g_error_free(error);
        return;
    }
    int width = gdk_pixbuf_get_width(pixbuf);
    if (width > 700) {
        int height = gdk_pixbuf_get_height(pixbuf);
        double ratio = 700.0 / width;
        GdkPixbuf *scaled = gdk_pixbuf_scale_simple(pixbuf, 700, (int)(height * ratio),
                                                     GDK_INTERP_BILINEAR);
        g_object_unref(pixbuf);
        pixbuf = scaled;
    }
    GtkTextIter iter;
    gtk_text_buffer_get_iter_at_mark(app->text_buffer, &iter,
                                     gtk_text_buffer_get_insert(app->text_buffer));
    gtk_text_buffer_insert_pixbuf(app->text_buffer, &iter, pixbuf);
    gtk_text_buffer_insert(app->text_buffer, &iter, "\n", -1);
    g_object_unref(pixbuf);
    app->image_counter++;
    update_status(app, "Image inserted", FALSE);
}

/* ----- Command Parsing ----- */
static void execute_command(TexxoEditor *app, const char *cmd) {
    char *cmd_copy = g_strdup(cmd);
    char *token = strtok(cmd_copy, " ");
    if (!token) { g_free(cmd_copy); return; }

    char *args = cmd_copy + strlen(token) + 1;
    while (*args == ' ') args++;

    /* Map commands */
    if (strcasecmp(token, "bo") == 0 || strcasecmp(token, "bold") == 0)
        apply_bold(app);
    else if (strcasecmp(token, "it") == 0 || strcasecmp(token, "italic") == 0)
        apply_italic(app);
    else if (strcasecmp(token, "ul") == 0 || strcasecmp(token, "underline") == 0)
        apply_underline(app);
    else if (strcasecmp(token, "st") == 0 || strcasecmp(token, "strike") == 0)
        apply_strikethrough(app);
    else if (strcasecmp(token, "tc") == 0 || strcasecmp(token, "color") == 0)
        apply_color(app, *args ? args : "white");
    else if (strcasecmp(token, "hh") == 0 || strcasecmp(token, "highlight") == 0)
        apply_highlight(app, *args ? args : "yellow");
    else if (strcasecmp(token, "ff") == 0 || strcasecmp(token, "font") == 0)
        apply_font_family(app, args);
    else if (strcasecmp(token, "fs") == 0 || strcasecmp(token, "fontsize") == 0)
        apply_font_size(app, atoi(args));
    else if (strcasecmp(token, "ft") == 0 || strcasecmp(token, "fontstyle") == 0)
        apply_font_style(app, args);
    else if (strcasecmp(token, "align") == 0) {
        if (strcasecmp(args, "left") == 0)
            apply_alignment(app, GTK_JUSTIFY_LEFT);
        else if (strcasecmp(args, "center") == 0)
            apply_alignment(app, GTK_JUSTIFY_CENTER);
        else if (strcasecmp(args, "right") == 0)
            apply_alignment(app, GTK_JUSTIFY_RIGHT);
    }
    else if (strcasecmp(token, "indent") == 0)
        indent_selection(app);
    else if (strcasecmp(token, "outdent") == 0)
        outdent_selection(app);
    else if (strcasecmp(token, "rm") == 0 || strcasecmp(token, "reset") == 0)
        clear_formatting(app);
    else if (strcasecmp(token, "new") == 0)
        new_document(app);
    else if (strcasecmp(token, "open") == 0)
        open_file(app, args);
    else if (strcasecmp(token, "save") == 0)
        save_file(app, args);
    else if (strcasecmp(token, "img") == 0 || strcasecmp(token, "image") == 0)
        insert_image(app, args);
    else if (strcasecmp(token, "find") == 0) {
        GtkTextIter start, match_start, match_end;
        gtk_text_buffer_get_iter_at_mark(app->text_buffer, &start,
                                         gtk_text_buffer_get_insert(app->text_buffer));
        if (gtk_text_iter_forward_search(&start, args, 0, &match_start, &match_end, NULL)) {
            gtk_text_buffer_select_range(app->text_buffer, &match_start, &match_end);
            GtkTextMark *mark = gtk_text_buffer_create_mark(app->text_buffer, NULL, &match_end, FALSE);
            gtk_text_view_scroll_to_mark(GTK_TEXT_VIEW(app->text_view), mark, 0.0, FALSE, 0.5, 0.5);
            gtk_text_buffer_delete_mark(app->text_buffer, mark);
            update_status(app, "Found", FALSE);
        } else {
            update_status(app, "Not found", TRUE);
        }
    }
    else if (strcasecmp(token, "replace") == 0) {
        char *old_text = strtok(args, " ");
        char *new_text = strtok(NULL, "");
        if (old_text && new_text) {
            GtkTextIter start, end;
            if (gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end)) {
                char *sel = gtk_text_buffer_get_text(app->text_buffer, &start, &end, FALSE);
                char *rep = g_strjoinv(new_text, g_strsplit(sel, old_text, -1));
                gtk_text_buffer_delete(app->text_buffer, &start, &end);
                gtk_text_buffer_insert(app->text_buffer, &start, rep, -1);
                g_free(sel);
                g_free(rep);
            }
        }
    }
    else if (strcasecmp(token, "sa") == 0 || strcasecmp(token, "selectall") == 0) {
        GtkTextIter start_iter, end_iter;
        gtk_text_buffer_get_start_iter(app->text_buffer, &start_iter);
        gtk_text_buffer_get_end_iter(app->text_buffer, &end_iter);
        gtk_text_buffer_select_range(app->text_buffer, &start_iter, &end_iter);
    }
    else if (strcasecmp(token, "del") == 0 || strcasecmp(token, "delete") == 0) {
        GtkTextIter start, end;
        if (gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end))
            gtk_text_buffer_delete(app->text_buffer, &start, &end);
    }
    else if (strcasecmp(token, "cp") == 0 || strcasecmp(token, "copy") == 0) {
        GtkTextIter start, end;
        if (gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end)) {
            char *text = gtk_text_buffer_get_text(app->text_buffer, &start, &end, FALSE);
            GtkClipboard *clipboard = gtk_clipboard_get(GDK_SELECTION_CLIPBOARD);
            gtk_clipboard_set_text(clipboard, text, -1);
            g_free(text);
        }
    }
    else if (strcasecmp(token, "cut") == 0) {
        GtkTextIter start, end;
        if (gtk_text_buffer_get_selection_bounds(app->text_buffer, &start, &end)) {
            char *text = gtk_text_buffer_get_text(app->text_buffer, &start, &end, FALSE);
            GtkClipboard *clipboard = gtk_clipboard_get(GDK_SELECTION_CLIPBOARD);
            gtk_clipboard_set_text(clipboard, text, -1);
            gtk_text_buffer_delete(app->text_buffer, &start, &end);
            g_free(text);
        }
    }
    else if (strcasecmp(token, "paste") == 0) {
        GtkClipboard *clipboard = gtk_clipboard_get(GDK_SELECTION_CLIPBOARD);
        gchar *text = gtk_clipboard_wait_for_text(clipboard);
        if (text) {
            gtk_text_buffer_insert_at_cursor(app->text_buffer, text, -1);
            g_free(text);
        }
    }
    else if (strcasecmp(token, "help") == 0) {
        gtk_text_buffer_set_text(app->text_buffer,
            "Texxo C Edition Commands:\n"
            "bo / bold - Bold\n"
            "it / italic - Italic\n"
            "ul / underline - Underline\n"
            "st / strike - Strikethrough\n"
            "tc / color <name|#hex> - Text color\n"
            "hh / highlight <name|#hex> - Highlight\n"
            "ff / font <family> - Change font family\n"
            "fs / fontsize <size> - Change font size\n"
            "ft / fontstyle <style> - Apply preset style\n"
            "align <left|center|right> - Alignment\n"
            "indent / outdent - Indent/outdent\n"
            "rm / reset - Clear formatting\n"
            "new - New document\n"
            "open [file] - Open file\n"
            "save [file] - Save file\n"
            "img / image [file] - Insert image\n"
            "find <text> - Find text\n"
            "replace <old> <new> - Replace in selection\n"
            "sa / selectall - Select all\n"
            "del / delete - Delete selection\n"
            "cp / copy - Copy\n"
            "cut / paste - Cut/paste\n"
            "help - Show this help", -1);
    }
    else {
        update_status(app, "Unknown command", TRUE);
    }
    g_free(cmd_copy);
    update_line_numbers(app);
    update_status_bar(app);
}

/* ----- Callbacks ----- */
static void on_cmd_entry_activate(GtkEntry *entry, TexxoEditor *app) {
    const char *cmd = gtk_entry_get_text(entry);
    if (strlen(cmd) > 0)
        execute_command(app, cmd);
    gtk_entry_set_text(entry, "");
}

static void on_text_buffer_changed(GtkTextBuffer *buffer, TexxoEditor *app) {
    update_line_numbers(app);
    update_status_bar(app);
}

/* ----- Widget Creation ----- */
static void create_tags(TexxoEditor *app) {
    gtk_text_buffer_create_tag(app->text_buffer, "bold",
                                "weight", PANGO_WEIGHT_BOLD, NULL);
    gtk_text_buffer_create_tag(app->text_buffer, "italic",
                                "style", PANGO_STYLE_ITALIC, NULL);
    gtk_text_buffer_create_tag(app->text_buffer, "underline",
                                "underline", PANGO_UNDERLINE_SINGLE, NULL);
    gtk_text_buffer_create_tag(app->text_buffer, "strikethrough",
                                "strikethrough", TRUE, NULL);
    gtk_text_buffer_create_tag(app->text_buffer, "align_left",
                                "justification", GTK_JUSTIFY_LEFT, NULL);
    gtk_text_buffer_create_tag(app->text_buffer, "align_center",
                                "justification", GTK_JUSTIFY_CENTER, NULL);
    gtk_text_buffer_create_tag(app->text_buffer, "align_right",
                                "justification", GTK_JUSTIFY_RIGHT, NULL);
}

static void activate(GtkApplication *gtk_app, gpointer user_data) {
    TexxoEditor *app = g_new0(TexxoEditor, 1);
    app->theme = 0;
    app->bookmarks = g_hash_table_new_full(g_str_hash, g_str_equal, g_free, g_free);

    /* Window */
    app->window = gtk_application_window_new(gtk_app);
    gtk_window_set_title(GTK_WINDOW(app->window), "Texxo Pro - C Edition");
    gtk_window_set_default_size(GTK_WINDOW(app->window), 1100, 800);

    /* Main vertical box */
    app->main_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    gtk_container_add(GTK_CONTAINER(app->window), app->main_vbox);

    /* Command bar */
    GtkWidget *cmd_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 5);
    gtk_widget_set_margin_start(cmd_box, 10);
    gtk_widget_set_margin_end(cmd_box, 10);
    gtk_widget_set_margin_top(cmd_box, 10);
    gtk_widget_set_margin_bottom(cmd_box, 5);

    GtkWidget *cmd_label = gtk_label_new("Command:");
    gtk_box_pack_start(GTK_BOX(cmd_box), cmd_label, FALSE, FALSE, 0);

    app->cmd_entry = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(app->cmd_entry), "Type command...");
    g_signal_connect(app->cmd_entry, "activate", G_CALLBACK(on_cmd_entry_activate), app);
    gtk_box_pack_start(GTK_BOX(cmd_box), app->cmd_entry, TRUE, TRUE, 0);

    GtkWidget *run_btn = gtk_button_new_with_label("Run");
    g_signal_connect_swapped(run_btn, "clicked", G_CALLBACK(on_cmd_entry_activate), app);
    gtk_box_pack_start(GTK_BOX(cmd_box), run_btn, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(app->main_vbox), cmd_box, FALSE, FALSE, 0);

    /* Status label */
    app->status_label = gtk_label_new(NULL);
    gtk_label_set_markup(GTK_LABEL(app->status_label),
                         "<span foreground='#b7d2ff'>Ready</span>");
    gtk_widget_set_margin_start(app->status_label, 10);
    gtk_box_pack_start(GTK_BOX(app->main_vbox), app->status_label, FALSE, FALSE, 0);

    /* Editor area with line numbers */
    GtkWidget *hpaned = gtk_paned_new(GTK_ORIENTATION_HORIZONTAL);
    gtk_box_pack_start(GTK_BOX(app->main_vbox), hpaned, TRUE, TRUE, 0);

    /* Line numbers */
    app->line_numbers_view = gtk_text_view_new();
    gtk_text_view_set_editable(GTK_TEXT_VIEW(app->line_numbers_view), FALSE);
    gtk_text_view_set_cursor_visible(GTK_TEXT_VIEW(app->line_numbers_view), FALSE);
    gtk_widget_set_size_request(app->line_numbers_view, 60, -1);
    GtkCssProvider *provider = gtk_css_provider_new();
    gtk_css_provider_load_from_data(provider,
        "textview { background-color: #0a1a3a; color: #4a6a8a; }", -1, NULL);
    gtk_style_context_add_provider(gtk_widget_get_style_context(app->line_numbers_view),
                                   GTK_STYLE_PROVIDER(provider),
                                   GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    g_object_unref(provider);
    gtk_paned_pack1(GTK_PANED(hpaned), app->line_numbers_view, FALSE, FALSE);

    /* Text view */
    app->scrolled_window = gtk_scrolled_window_new(NULL, NULL);
    app->text_view = gtk_text_view_new();
    gtk_container_add(GTK_CONTAINER(app->scrolled_window), app->text_view);
    gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(app->text_view), GTK_WRAP_WORD);
    gtk_paned_pack2(GTK_PANED(hpaned), app->scrolled_window, TRUE, TRUE);

    app->text_buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(app->text_view));
    g_signal_connect(app->text_buffer, "changed", G_CALLBACK(on_text_buffer_changed), app);
    g_signal_connect(app->text_buffer, "mark-set", G_CALLBACK(update_status_bar), app);

    /* Default font */
    app->default_font = pango_font_description_from_string("Consolas 14");
    gtk_widget_override_font(app->text_view, app->default_font);

    create_tags(app);

    /* Status bar */
    app->status_bar = gtk_label_new("Lines: 1 | Words: 0 | Characters: 0 | Position: 1:0");
    gtk_label_set_xalign(GTK_LABEL(app->status_bar), 0);
    gtk_widget_set_margin_start(app->status_bar, 10);
    gtk_box_pack_end(GTK_BOX(app->main_vbox), app->status_bar, FALSE, FALSE, 0);

    /* Apply dark theme (CSS) */
    GtkCssProvider *theme_provider = gtk_css_provider_new();
    gtk_css_provider_load_from_data(theme_provider,
        "window { background-color: #071b38; }\n"
        "textview { background-color: #0f2345; color: white; }\n"
        "entry { background-color: #122846; color: white; }\n"
        "button { background-color: #1f508b; color: white; }\n"
        "label { color: #b7d2ff; }", -1, NULL);
    gtk_style_context_add_provider_for_screen(gdk_screen_get_default(),
                                              GTK_STYLE_PROVIDER(theme_provider),
                                              GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    g_object_unref(theme_provider);

    gtk_widget_show_all(app->window);
    update_line_numbers(app);
}

int main(int argc, char **argv) {
    GtkApplication *app = gtk_application_new("com.texxo.pro", G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    return status;
}
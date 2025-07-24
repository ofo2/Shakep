import subprocess
import os
import sys

APACHE_CONF_PATH = "/etc/apache2/sites-available/000-default.conf"
WEB_ROOT = "/var/www/html"
INDEX_HTML_PATH = os.path.join(WEB_ROOT, "index.html")

def run_command(command, check=True):
    print(f"تشغيل الأمر: {' '.join(command)}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0 and check:
        print(f"خطأ في الأمر: {' '.join(command)}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def install_apache():
    print("التحقق من وجود Apache2...")
    # تحقق إذا apache2 موجود
    try:
        run_command(["apache2ctl", "-v"])
        print("Apache2 مثبت بالفعل.")
    except FileNotFoundError:
        print("Apache2 غير مثبت، سيتم تثبيته الآن...")
        run_command(["sudo", "apt-get", "update"])
        run_command(["sudo", "apt-get", "install", "-y", "apache2"])
        print("تم تثبيت Apache2 بنجاح.")

def backup_file(file_path):
    backup_path = file_path + ".bak"
    if not os.path.exists(backup_path):
        print(f"إنشاء نسخة احتياطية من {file_path} باسم {backup_path}")
        run_command(["sudo", "cp", file_path, backup_path])
    else:
        print(f"النسخة الاحتياطية {backup_path} موجودة مسبقًا، لن يتم استبدالها.")

def modify_apache_conf():
    print(f"تعديل ملف إعدادات Apache: {APACHE_CONF_PATH}")
    backup_file(APACHE_CONF_PATH)

    # قراءة المحتوى الحالي
    with open(APACHE_CONF_PATH, "r") as file:
        content = file.readlines()

    new_content = []
    for line in content:
        if "DocumentRoot" in line:
            # تغيير مسار مجلد الويب إذا أردت، هنا نتركه كما هو
            new_content.append("    DocumentRoot /var/www/html\n")
        else:
            new_content.append(line)

    # إضافة إعدادات أمان إضافية (مثال)
    new_content.append("\n# إعدادات أمان مضافة تلقائياً\n")
    new_content.append("<Directory /var/www/html>\n")
    new_content.append("    Options Indexes FollowSymLinks\n")
    new_content.append("    AllowOverride None\n")
    new_content.append("    Require all granted\n")
    new_content.append("</Directory>\n")

    # كتابة الملف المعدل باستخدام sudo tee (لأن الملف محمي)
    temp_file = "/tmp/000-default.conf.tmp"
    with open(temp_file, "w") as tempf:
        tempf.writelines(new_content)

    print(f"كتابة الملف المعدل إلى {APACHE_CONF_PATH}")
    run_command(["sudo", "mv", temp_file, APACHE_CONF_PATH])
    run_command(["sudo", "chown", "root:root", APACHE_CONF_PATH])
    run_command(["sudo", "chmod", "644", APACHE_CONF_PATH])
    print("تم تعديل ملف إعدادات Apache بنجاح.")

def create_index_html():
    print(f"إنشاء صفحة HTML بسيطة في {INDEX_HTML_PATH}")
    html_content = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>مرحبا بك في Apache</title>
</head>
<body>
    <h1>تم إعداد Apache بنجاح!</h1>
    <p>هذه صفحة افتراضية تستضيفها خادم Apache.</p>
</body>
</html>
"""
    temp_html = "/tmp/index.html.tmp"
    with open(temp_html, "w") as f:
        f.write(html_content)

    run_command(["sudo", "mv", temp_html, INDEX_HTML_PATH])
    run_command(["sudo", "chown", "www-data:www-data", INDEX_HTML_PATH])
    run_command(["sudo", "chmod", "644", INDEX_HTML_PATH])
    print("تم إنشاء صفحة HTML بنجاح.")

def restart_apache():
    print("إعادة تشغيل خدمة Apache...")
    run_command(["sudo", "systemctl", "restart", "apache2"])
    print("تم إعادة تشغيل Apache بنجاح.")

def main():
    print("بدء إعداد Apache تلقائيًا...")
    install_apache()
    modify_apache_conf()
    create_index_html()
    restart_apache()
    print("تم إعداد وتشغيل Apache بنجاح! يمكنك الآن زيارة http://localhost")

if __name__ == "__main__":
    main()
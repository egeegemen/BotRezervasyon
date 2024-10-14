from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Renk sabitleri
class Colors:
    GREEN = "\033[92m"  # Yeşil
    RED = "\033[91m"    # Kırmızı
    YELLOW = "\033[93m" # Sarı
    RESET = "\033[0m"   # Varsayılan rengi sıfırla

def initialize_driver():
    service = Service("C:\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    return driver

def login(driver):
    login_url = "https://online.spor.istanbul/uyegiris"
    driver.get(login_url)

    # Kullanıcı adı ve şifre alanlarını bulup dolduruyoruz
    username_input = driver.find_element(By.ID, "txtTCPasaport")  
    password_input = driver.find_element(By.ID, "txtSifre") 

    # Kullanıcı adı ve şifreyi giriyoruz
    username_input.send_keys("10367625808")
    password_input.send_keys("Muhammet.1036")

    # Giriş butonuna tıklıyoruz
    login_button = driver.find_element(By.ID, "btnGirisYap")
    login_button.click()
    print(Colors.GREEN + "Giriş Tamamlandı" + Colors.RESET)

    # Modal kapatma
    close_modal(driver)

def close_modal(driver):
    btn_kapat = driver.find_element(By.ID, "closeModal")
    checkbox = driver.find_element(By.ID, "checkBox")
    checkbox.click()
    btn_kapat.click()

def select_futbol(driver):
    # "Kiralamaya Yap" butonuna tıklıyoruz
    kiralama_yap_button = driver.find_element(By.ID, "contacttab6")
    kiralama_yap_button.click()

    # "Futbol" select kutusunu buluyoruz
    futbol_select_element = driver.find_element(By.ID, "ddlKiralikBransFiltre")
    futbol_select = Select(futbol_select_element)
    futbol_select.select_by_visible_text("FUTBOL")  # "Futbol" seçeneğini seçiyoruz
     
    # "Tesis" select kutusunu buluyoruz
    tesis_select_element = driver.find_element(By.ID, "ddlKiralikTesisFiltre")
    tesis_select = Select(tesis_select_element)
    tesis_select.select_by_visible_text("EDİRNEKAPI SPOR TESİSİ")  # "Tesis" seçeneğini seçiyoruz

    # "Bul" butonuna tıklıyoruz
    kiralama_yap_button = driver.find_element(By.ID, "pageContent_ucUrunArama_lbtnKiralikAra")
    kiralama_yap_button.click()

def check_availability(driver, hedef_tarih, hedef_saat):
    # Gün başlıklarını buluyoruz (örneğin: 'Salı, 12 Ekim')
    gunler = driver.find_elements(By.CLASS_NAME, "panel-title")

    # İlgili tarih için kontrol yapıyoruz
    for gun in gunler:
        if hedef_tarih in gun.text:  # İlgili tarihi bulduk
            # handle_availability fonksiyonu true/false döndürsün
            if handle_availability(gun, hedef_tarih, hedef_saat):
                print(Colors.GREEN + f"{hedef_tarih} için rezervasyon tamamlandı." + Colors.RESET)
                return  # Rezervasyon yapıldıysa döngüyü kır

    print(Colors.RED + f"{hedef_tarih} için rezervasyon yapılacak başka bir tarih bulunamadı." + Colors.RESET)

def handle_availability(gun, hedef_tarih, hedef_saat):
    # Günü bulduktan sonra, o günün altındaki panel-body div'ini kontrol ediyoruz
    try:
        parent_div = gun.find_element(By.XPATH, "./ancestor::div[@class='panel-heading']/following-sibling::div[@class='panel-body']")
        
        # Div'in içinde bir şey var mı diye kontrol ediyoruz (boş olup olmadığını kontrol)
        if len(parent_div.text.strip()) == 0:
            print(Colors.RED + f"{hedef_tarih} boş, rezervasyon yapılacak başka bir tarih bulunamadı." + Colors.RESET)
            return False  # Eğer div boşsa false döndür

        print(Colors.GREEN + f"{hedef_tarih} dolu, saat aralıkları kontrol ediliyor." + Colors.RESET)

        # Doluysa, saat aralıklarını kontrol et
        time_slots = parent_div.find_elements(By.CLASS_NAME, "lblStyle")

        # Saat aralığına göre rezervasyon butonunu bulup tıklıyoruz
        for slot in time_slots:
            if slot.text == hedef_saat:  # İlgili saat aralığını bulduk
                print(Colors.GREEN + f"{hedef_saat} saat aralığı bulundu." + Colors.RESET)
                rezervasyon_button = slot.find_element(By.XPATH, "./following-sibling::a[@title='Rezervasyon']")
                rezervasyon_button.click()  # Rezervasyon butonuna tıklıyoruz
                print(Colors.GREEN + "Rezervasyon yapıldı." + Colors.RESET)
                return True  # Rezervasyon yapıldıysa true döndür

        print(Colors.RED + f"{hedef_saat} saat aralığı bulunamadı." + Colors.RESET)
        return False  # Saat aralığı bulunamadıysa false döndür

    except Exception as e:
        print(Colors.RED + f"{hedef_tarih} için bir hata oluştu: {e}" + Colors.RESET)
        return False  # Hata oluşursa false döndür

def handle_alert(driver):
    try:
        alert = driver.switch_to.alert
        print(Colors.YELLOW + alert.text + Colors.RESET)  # Uyarı mesajını görmek isterseniz
        alert.accept()  # "Tamam" butonuna basmak için accept() kullanıyoruz
        print(Colors.GREEN + "Uyarı mesajı kabul edildi." + Colors.RESET)
    except:
        print(Colors.RED + "Alert bulunamadı." + Colors.RESET)

def handle_captcha(driver):
    # CAPTCHA alanını bulmak için uygun bir seçim yapın
    try:

        # CAPTCHA görüntüsünü bekliyoruz
        captcha_image = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "pageContent_captchaImage"))
        )
        print(Colors.YELLOW + "Lütfen CAPTCHA kodunu girin ve devam edin." + Colors.RESET)
        
        # Kullanıcıdan CAPTCHA kodunu girmesini isteyin
        captcha_input = input("CAPTCHA kodunu girin: ")

        # CAPTCHA kodunu girmek için uygun alanı bul
        captcha_field = driver.find_element(By.ID, "pageContent_txtCaptchaText")
        captcha_field.send_keys(captcha_input)

        # "Sepete Ekle" butonuna tıklayın
        add_to_cart_button = driver.find_element(By.ID, "pageContent_lbtnSepeteEkle")  # Butonun ID'sini güncelleyin
        add_to_cart_button.click()

        print(Colors.GREEN + "Sepete Eklendi." + Colors.RESET)

    except Exception as e:
        print(Colors.RED + f"CAPTCHA ile ilgili bir hata oluştu: {e}" + Colors.RESET)


def main():
    driver = initialize_driver()
    login(driver)
    select_futbol(driver)

    # Hedef tarih ve saat aralığını buradan ayarlıyoruz
    hedef_tarih = "15.10.2024"  # Hedef tarih (örneğin: "12 Ekim")
    hedef_saat = "13:00 - 14:00"  # Aranan saat aralığı

    check_availability(driver, hedef_tarih, hedef_saat)

    # Önce alerti kontrol et, ardından CAPTCHA'yı çöz
    handle_alert(driver)
    handle_captcha(driver)  # CAPTCHA kontrolü buraya ekleniyor

    time.sleep(100)
    driver.quit()

if __name__ == "__main__":
    main()

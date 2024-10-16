from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

# Renk sabitleri
class Colors:
    GREEN = "\033[92m"  # Yeşil
    RED = "\033[91m"    # Kırmızı
    YELLOW = "\033[93m" # Sarı
    BLUE = "\033[94m"   # Mavi
    BRIGHT_MAGENTA = "\033[95m"
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

def check_availability(driver, hedef_tarih, hedef_saatler):
    # Gün başlıklarını buluyoruz (örneğin: 'Salı, 12 Ekim')
    gunler = driver.find_elements(By.CLASS_NAME, "panel-title")

    # İlgili tarih için kontrol yapıyoruz
    for gun in gunler:
        if hedef_tarih in gun.text:  # İlgili tarihi bulduk
            # handle_availability fonksiyonu true/false döndürsün
            if handle_availability(gun, hedef_tarih, hedef_saatler):
                return True # Rezervasyon yapıldıysa döngüyü kır

def handle_availability(gun, hedef_tarih, hedef_saatler):
    # Günü bulduktan sonra, o günün altındaki panel-body div'ini kontrol ediyoruz
    try:
        parent_div = gun.find_element(By.XPATH, "./ancestor::div[@class='panel-heading']/following-sibling::div[@class='panel-body']")
        
        # Div'in içinde bir şey var mı diye kontrol ediyoruz (boş olup olmadığını kontrol)
        if len(parent_div.text.strip()) == 0:
            print(Colors.RED + f"{hedef_tarih} boş, rezervasyon yapılacak başka bir tarih bulunamadı." + Colors.RESET)
            return False  # Eğer div boşsa false döndür
        
        current_time1 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(Colors.BLUE + f"{current_time1}" + Colors.GREEN+ f"- {hedef_tarih} dolu, saat aralıkları kontrol ediliyor." + Colors.RESET)

        # Doluysa, saat aralıklarını kontrol et
        time_slots = parent_div.find_elements(By.CLASS_NAME, "lblStyle")

        # Saat aralığına göre rezervasyon butonunu bulup tıklıyoruz
        for slot in time_slots:
            if slot.text in hedef_saatler:  # Eğer slot, hedef saatler listesindeki bir aralıkla eşleşiyorsa
                print(Colors.GREEN + f"{slot.text} saat aralığı bulundu." + Colors.RESET)
                try:
                    # Rezervasyon butonunu bulmaya çalışıyoruz
                    rezervasyon_button = slot.find_element(By.XPATH, "./following-sibling::a[@title='Rezervasyon']")
                    current_time2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    rezervasyon_button.click()  # Rezervasyon butonuna tıklıyoruz
                    print(Colors.BLUE + f"{current_time2}" + Colors.GREEN + f"- Rezervasyona Tıklandı." + Colors.RESET)
                    return True  # Rezervasyon yapıldıysa true döndür
                except Exception as e:
                    # Eğer buton bulunamazsa, hata mesajı bas ve bir sonraki slot'a geç
                    print(Colors.YELLOW + f"{slot.text} saat aralığı dolu olabilir, sıradaki saat aralığına geçiliyor." + Colors.RESET)
                    continue  # Bir sonraki saat aralığına geç


        print(Colors.RED + f"{hedef_saatler} saat aralığı bulunamadı." + Colors.RESET)
        return False  # Saat aralığı bulunamadıysa false döndür

    except Exception as e:
        print(Colors.RED + f"{hedef_tarih} için bir hata oluştu: {e}" + Colors.RESET)
        return False  # Hata oluşursa false döndür

def continuously_check_availability(driver, hedef_tarih, hedef_saatler, check_interval=1):
    print(Colors.YELLOW + f"Rezervasyonlar kontrol ediliyor... Her {check_interval} saniyede bir kontrol yapılacak." + Colors.RESET)
    
    while True:
        # Rezervasyonları kontrol et
        rezervasyon_yapildi = check_availability(driver, hedef_tarih, hedef_saatler)
        
        if rezervasyon_yapildi:
            print(Colors.GREEN + f"{hedef_tarih} için rezervasyondan sonra CAPTCHA'ya gecildi." + Colors.RESET)
            break  # Eğer rezervasyon başarılı olursa döngüyü kır ve durdur
        
        # Rezervasyonlar henüz yoksa belirli bir süre bekle ve tekrar dene
        print(Colors.YELLOW + f"{check_interval} saniye sonra tekrar denenecek..." + Colors.RESET)
        driver.refresh()
        time.sleep(check_interval)  # Belirtilen saniye kadar bekle

def handle_alert(driver):
    try:
        alert = driver.switch_to.alert
        print(Colors.BRIGHT_MAGENTA + alert.text + Colors.RESET)  # Uyarı mesajını görmek isterseniz
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
        print(Colors.YELLOW + "Lütfen CAPTCHA kodunu girin ve bu islem son bulsun" + Colors.RESET)
        
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
    print(Colors.GREEN + "Giriş Tamamlandı" + Colors.RESET)
    select_futbol(driver)
    print(Colors.GREEN + "Halisaha Secildi" + Colors.RESET)

    # Hedef tarih ve saat aralığını buradan ayarlıyoruz
    hedef_tarih = "17.10.2024"  # Hedef tarih (örneğin: "12 Ekim")
    hedef_saatler = ["07:00 - 08:00", "08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00"]  # Aranan saat aralıkları


    # Rezervasyonları sürekli kontrol eden fonksiyonu çağırıyoruz
    continuously_check_availability(driver, hedef_tarih, hedef_saatler)

    # Önce alerti kontrol et, ardından CAPTCHA'yı çöz
    handle_alert(driver)
    handle_captcha(driver)  # CAPTCHA kontrolü buraya ekleniyor

    time.sleep(100)
    driver.quit()

if __name__ == "__main__":
    main()

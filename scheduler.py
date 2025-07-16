# scheduler.py

from itertools import product
import ders_sections
import sys

class Scheduler:
    def __init__(self, programad):
        self.programad = programad
        self.dongu = True
        self.tum_dersler = [] 

    def program(self):
        semest_number, yil = ders_sections.kullanicidan_donem_secimi()
        semester_code = f"{yil}{semest_number}"
        yeni_ders = ders_sections.main(semester_code)
        if yeni_ders:
            self.tum_dersler.append(yeni_ders)
            print("\nDersiniz Başarıyla Eklendi...\n")
        else:
            print("Ders eklenemedi veya bulunamadı.")
        


    def uygun_programlari_olustur(self):
        all_combinations = list(product(*self.tum_dersler))
        uygun_programlar = []

        for kombinasyon in all_combinations:
            if not self.cakisma_var_mi(kombinasyon):
                uygun_programlar.append(kombinasyon)

        print(f"{len(uygun_programlar)} uygun program bulundu.")
        for i, program in enumerate(uygun_programlar, 1):
            print(f"\n--- Program {i} ---")
            for ders in program:
                print(f"Section {ders['section']} ({ders['instructor']})")
                for saat in ders["times"]:
                    print(" ", saat)

    def cakisma_var_mi(self, kombinasyon):
        zamanlar = set()
        for ders in kombinasyon:
            for gun_saat in ders["times"]:
                for gun, (tur, saat) in gun_saat.items():
                    if (gun, saat) in zamanlar:
                        return True
                    zamanlar.add((gun, saat))
        return False
    
    def menu(self):
        while True:
            print("")
            print("Lütfen Yapmak İstediğiniz İşlemi Giriniz:\n[1]-Ders Ekle\n[2]-Program Görüntüle\n[3]-Çıkış")
            secim = input("Lütfen Seçim Yapınız: ")
            print("")
            if secim == "1":
                self.program()
            elif secim == "2":
                self.uygun_programlari_olustur()
            elif secim == "3":
                self.cıkıs()
            
    def cıkıs(self):
        sys.exit()


if __name__ == "__main__":
    Sistem = Scheduler("Bilkent Uni")
    while Sistem.dongu:
        Sistem.menu()
        Sistem.dongu = False  # İsteğe bağlı olarak yeniden açabilirsin

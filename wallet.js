
import { TronWeb } from "https://esm.sh/tronweb@6.5.1";
document.getElementById("walletResult").innerText = "Kod yüklendi";
const button = document.getElementById("createWallet");
const result = document.getElementById("walletResult");

button.addEventListener("click", async () => {
  if (document.getElementById("backupPassword")) return;

  const label = document.createElement("p");
  label.textContent = "Yedekleme şifreni belirle (en az 12 karakter):";

  const password = document.createElement("input");
  password.id = "backupPassword";
  password.type = "password";
  password.autocomplete = "new-password";
  password.placeholder = "Güçlü bir şifre belirle";
  password.minLength = 12;
  password.style.cssText =
    "width:90%;padding:12px;margin:10px;border-radius:8px;";

  const confirm = document.createElement("button");
  confirm.textContent = "Cüzdanı Oluştur";

  result.replaceChildren(label, password, confirm);

  confirm.addEventListener("click", async () => {
    confirm.disabled = true;

    try {
      if (!window.crypto?.subtle) {
        throw new Error("Güvenli bağlantı gerekli.");
      }

      if (password.value.length < 12) {
        throw new Error("Şifre en az 12 karakter olmalı.");
      }

      const wallet = TronWeb.createRandom();
      const phrase = wallet.mnemonic.phrase;
      const address = wallet.address;

      const encoder = new TextEncoder();
      const salt = crypto.getRandomValues(new Uint8Array(16));
      const iv = crypto.getRandomValues(new Uint8Array(12));

      const material = await crypto.subtle.importKey(
        "raw",
        encoder.encode(password.value),
        "PBKDF2",
        false,
        ["deriveKey"]
      );

      const key = await crypto.subtle.deriveKey({
        name: "PBKDF2",
        salt,
        iterations: 310000,
        hash: "SHA-256"
      }, material, {
        name: "AES-GCM",
        length: 256
      }, false, ["encrypt"]);

      const encrypted = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv },
        key,
        encoder.encode(phrase)
      );

      const base64 = data =>
        btoa(String.fromCharCode(...new Uint8Array(data)));

      const backup = {
        version: 1,
        network: "TRON",
        address,
        salt: base64(salt),
        iv: base64(iv),
        encryptedMnemonic: base64(encrypted)
      };

      const file = new Blob(
        [JSON.stringify(backup, null, 2)],
        { type: "application/json" }
      );

      const url = URL.createObjectURL(file);
      const link = document.createElement("a");
      link.href = url;
      link.download = "cuzdan-yedegi.json";
      link.click();

      setTimeout(() => URL.revokeObjectURL(url), 2000);

      result.textContent =
        "Test cüzdanı oluşturuldu. Adres: " + address +
        " Şifreli yedek dosyası indirilmeye çalışıldı.";

    } catch (error) {
      result.textContent = "Hata: " + error.message;
    } finally {
      confirm.disabled = false;
    }
  });
});



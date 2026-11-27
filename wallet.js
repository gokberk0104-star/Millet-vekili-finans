
import { TronWeb } from "https://esm.sh/tronweb@6.5.1";

const button = document.getElementById("createWallet");
const result = document.getElementById("walletResult");

button.addEventListener("click", async () => {
  button.disabled = true;

  try {
    if (!window.crypto?.subtle) {
      throw new Error("Güvenli tarayıcı bağlantısı gerekli.");
    }

    const password = prompt(
      "Şifreli yedekleme için güçlü bir şifre belirle:"
    );

    if (!password || password.length < 12) {
      throw new Error("En az 12 karakterli bir şifre kullan.");
    }

    result.textContent = "Cüzdan oluşturuluyor...";

    const wallet = TronWeb.createRandom();
    const phrase = wallet.mnemonic.phrase;
    const address = wallet.address;

    const encoder = new TextEncoder();
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const iv = crypto.getRandomValues(new Uint8Array(12));

    const keyMaterial = await crypto.subtle.importKey(
      "raw",
      encoder.encode(password),
      "PBKDF2",
      false,
      ["deriveKey"]
    );

    const key = await crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt,
        iterations: 310000,
        hash: "SHA-256"
      },
      keyMaterial,
      {
        name: "AES-GCM",
        length: 256
      },
      false,
      ["encrypt"]
    );

    const encrypted = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv },
      key,
      encoder.encode(phrase)
    );

    const toBase64 = bytes =>
      btoa(String.fromCharCode(...new Uint8Array(bytes)));

    const backup = {
      version: 1,
      network: "TRON",
      address,
      salt: toBase64(salt),
      iv: toBase64(iv),
      encryptedMnemonic: toBase64(encrypted)
    };

    const file = new Blob(
      [JSON.stringify(backup, null, 2)],
      { type: "application/json" }
    );

    const link = document.createElement("a");
    link.href = URL.createObjectURL(file);
    link.download = "millet-vekilim-cuzdan-yedegi.json";
    link.click();

    setTimeout(() => URL.revokeObjectURL(link.href), 1000);

    result.textContent =
      "Cüzdan oluşturuldu. Adres: " + address +
      "\nŞifreli yedekleme dosyası indirildi. " +
      "Dosyayı ve şifreni ayrı ayrı güvenli yerlerde sakla.";

  } catch (error) {
    result.textContent = "Hata: " + error.message;
  } finally {
    button.disabled = false;
  }
});


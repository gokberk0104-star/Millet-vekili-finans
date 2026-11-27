
import { TronWeb } from "https://esm.sh/tronweb@6.1.0";

const button = document.getElementById("createWallet");
const result = document.getElementById("walletResult");

button.addEventListener("click", async () => {
  button.disabled = true;
  result.textContent = "Cüzdan oluşturuluyor...";

  try {
    const wallet = TronWeb.createRandom();

    const address = wallet.address;
    const recoveryPhrase = wallet.mnemonic.phrase;

    result.innerHTML = "";

    const title = document.createElement("h3");
    title.textContent = "Cüzdanın oluşturuldu!";

    const addressLabel = document.createElement("p");
    addressLabel.textContent = "Cüzdan adresin:";

    const addressValue = document.createElement("p");
    addressValue.textContent = address;

    const phraseLabel = document.createElement("p");
    phraseLabel.textContent =
      "12 kelimelik kurtarma ifaden (gizli tut):";

    const phraseValue = document.createElement("p");
    phraseValue.textContent = recoveryPhrase;

    const warning = document.createElement("p");
    warning.textContent =
      "Bu kelimeleri kağıda yaz ve güvenli yerde sakla. " +
      "Kimseyle paylaşma. Sayfayı kapatırsan tekrar gösterilemez.";

    result.append(
      title,
      addressLabel,
      addressValue,
      phraseLabel,
      phraseValue,
      warning
    );

  } catch (error) {
    result.textContent = "Cüzdan oluşturulamadı: " + error.message;
  } finally {
    button.disabled = false;
  }
});

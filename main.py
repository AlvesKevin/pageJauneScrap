import time
import json
import atexit
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Répertoire où les données de profil seront stockées
profile_directory = r'C:\Users\Kévin\PycharmProjects\pagesjaune\profil'

# Chemin du fichier de sauvegarde des informations des entreprises
output_file = 'entreprises.json'

# Options du navigateur
options = Options()
options.add_argument(f'user-data-dir={profile_directory}')

# Définir l'en-tête HTTP
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-infobars')
options.add_argument('--disable-web-security')
options.add_argument('--disable-site-isolation-trials')
options.add_argument('--no-sandbox')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')

# Ajouter un en-tête User-Agent pour éviter la détection automatisée
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36')

# Initialisation du service et du navigateur
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# Configuration de l'attente explicite pour le chargement des éléments
wait = WebDriverWait(driver, 80)

# URL des Pages Jaunes pour la recherche de restaurants au Mans
url = 'https://www.pagesjaunes.fr/annuaire/le-mans-72/restaurants'

# Liste pour stocker les informations des entreprises
companies = []


# Fonction pour enregistrer les informations des entreprises dans un fichier JSON
def save_companies():
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(companies, file, ensure_ascii=False, indent=4)


# S'assurer que les informations sont sauvegardées à la fin de l'exécution du script
atexit.register(save_companies)


def extract_company_info():
    # Recherche des résultats de la recherche
    results = driver.find_elements(By.XPATH, '//li[contains(@class, "bi-generic")]')

    # Nombre maximum d'entreprises à extraire
    max_companies = 268

    # Parcours des résultats
    for i in range(min(max_companies, len(results))):
        # Extraction du nom de l'entreprise
        results = driver.find_elements(By.XPATH, '//li[contains(@class, "bi-generic")]')
        name_element = results[i].find_element(By.CSS_SELECTOR, 'h3')
        name = name_element.text

        # Clique sur le nom de l'entreprise pour accéder à la page de détails
        name_element.click()

        # Attente que la page de détails se charge
        time.sleep(randint(10, 15))

        # Extraction des informations de l'entreprise
        company_info = {'Nom': name}

        # Extraction du numéro de téléphone
        try:
            # Clique sur le lien "Afficher le numéro" pour révéler le numéro de téléphone
            show_number_button = driver.find_element(By.CSS_SELECTOR, 'a.fantomas.btn.hidden-phone.btn_ico_left.btn_tertiary.pj-lb.pj-link')
            show_number_button.click()

            # Attente que le numéro de téléphone soit affiché
            time.sleep(randint(1, 3))

            # Extraction du numéro de téléphone
            phone_element = driver.find_element(By.CSS_SELECTOR, 'span.coord-numero.noTrad')
            phone = phone_element.text.strip()
            company_info['Téléphone'] = phone
        except:
            company_info['Téléphone'] = 'Non disponible'

        # Extraction de la localisation
        try:
            location = driver.find_element(By.CSS_SELECTOR, 'div.address-container a.teaser-item.black-icon.address').text
            company_info['Localisation'] = location
        except:
            company_info['Localisation'] = 'Non disponible'

        # Extraction du site web
        try:
            # Clique sur le lien du site internet pour accéder à la page correspondante
            website_element = driver.find_element(By.CSS_SELECTOR, 'div.lvs-container.marg-btm-s a.teaser-item.black-icon.pj-lb.pj-link')
            time.sleep(randint(1, 3))
            website_element.click()
            website = website_element.get_attribute('href')
            company_info['Site Web'] = website
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()
            # Switch back à la page de détails de l'entreprise
            driver.switch_to.window(driver.window_handles[0])
        except:
            company_info['Site Web'] = 'Non disponible'

        # Ajout des informations de l'entreprise à la liste
        companies.append(company_info)

        # Sauvegarde des informations des entreprises après chaque extraction
        save_companies()

        # Retour à la page des résultats de recherche
        driver.back()

        # Attente que les résultats de recherche se chargent
        time.sleep(randint(10, 15))


# Ouverture de l'URL initiale
driver.get(url)

# Validation automatique des cookies (si la bannière de cookies est présente)
try:
    cookie_button = wait.until(EC.element_to_be_clickable((By.ID, 'didomi-notice-agree-button')))
    cookie_button.click()
except:
    pass

while True:
    # Extraction des informations des entreprises de la page courante
    extract_company_info()

    # Vérification de l'existence d'une page suivante
    next_button = driver.find_element(By.ID, 'pagination-next')
    if not next_button.is_enabled():
        break

    # Clique sur le bouton "Suivant" pour accéder à la page suivante
    next_button.click()

    # Attente que la page suivante se charge
    time.sleep(randint(10, 15))

# Fermeture du navigateur
driver.quit()
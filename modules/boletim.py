import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os
import logging
from modules.utils import load_json_data, create_json

def get_updated_boletim_info():
    """
    Obtém as informações do boletim mais recente do site usando XPath específico
    Retorna um dicionário com link e data ou None se não encontrar
    """
    
    try:
        url = "https://www.ndu.net.br/boletim"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Navegar usando a estrutura do XPath: /html/body/div[4]/ul[1]/li[1]/a
        body = soup.find('body')
        if not body:
            logging.warning("Tag <body> não encontrada")
            return None
        
        # Encontrar a div[4] (índice 3 em zero-based)
        divs = body.find_all('div', recursive=False)
        if len(divs) < 4:
            logging.warning(f"Menos de 4 divs no body. Encontradas: {len(divs)}")
            return None
        
        target_div = divs[3]  # div[4] do XPath
        # logging.info(f"Div alvo encontrada: {target_div}")
        
        # Encontrar o primeiro ul dentro da div
        uls = target_div.find_all('ul', recursive=False)
        if not uls:
            logging.warning("Nenhum <ul> encontrado na div alvo")
            return None
        
        target_ul = uls[0]  # ul[1] do XPath
        # logging.info(f"UL alvo encontrada: {target_ul}")
        
        # Encontrar o primeiro li dentro do ul
        lis = target_ul.find_all('li', recursive=False)
        if not lis:
            logging.warning("Nenhum <li> encontrado no UL alvo")
            return None
        
        target_li = lis[0]  # li[1] do XPath
        # logging.info(f"LI alvo encontrada: {target_li}")
        
        # Encontrar o link dentro do li
        boletim_link = target_li.find('a', href=True)
        if not boletim_link:
            logging.warning("Nenhum link <a> encontrado no LI alvo")
            return None
        
        logging.info(f"Link do boletim encontrado: {boletim_link}")
        
        # Verificar se o texto começa com data no formato dd/mm/yyyy
        link_text = boletim_link.get_text().strip()
        logging.info(f"Texto do link: '{link_text}'")
        
        date_pattern = r'^\d{2}/\d{2}/\d{4}'
        match = re.match(date_pattern, link_text)
        
        if match:
            date_str = match.group()
            try:
                # Converter a data para objeto datetime
                boletim_date = datetime.strptime(date_str, '%d/%m/%Y')
                
                
                logging.info(f"Boletim encontrado - Data: {date_str}, URL: {boletim_link['href']}")
                
                return {
                    "redirect": boletim_link['href'],
                    "date": boletim_date,
                    "date_str": date_str,
                }
            except ValueError:
                logging.warning(f"Formato de data inválido no boletim: {date_str}")
        else:
            logging.warning(f"Texto do link não começa com data no formato dd/mm/yyyy: '{link_text}'")
        
        logging.warning("Nenhum boletim válido encontrado")
        return None
        
    except requests.RequestException as e:
        logging.error(f"Erro ao acessar o site: {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return None

def has_matching_boletim_link(boletim_url):
    """
    Verifica se o link do boletim já existe no arquivo JSON local
    """
    
    try:
        # Carregar o arquivo JSON existente
        json_file_path = "files/boletim_info.json"
        
        if not os.path.exists(json_file_path):
            logging.info(f"não existe dir: {json_file_path}")
            return False
        
        data = load_json_data(json_file_path)
        # Verificar se o link já existe no arquivo
        return data.get("link") == boletim_url
        
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    except Exception as e:
        logging.info(f"Erro ao verificar boletim: {e}")
        return False
    
def download_pdf(pdf_url):
    """
    Faz o download do arquivo PDF
    """
    
    try:
        filename = "Boletim.pdf"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(pdf_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Criar diretório para PDFs se não existir
        pdf_dir = "files"
        os.makedirs(pdf_dir, exist_ok=True)
        
        pdf_path = os.path.join(pdf_dir, filename)
        
        # Salvar o arquivo PDF
        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return pdf_path
        
    except requests.RequestException as e:
        logging.info(f"Erro ao baixar PDF: {e}")
        return None
    except Exception as e:
        logging.info(f"Erro inesperado ao baixar PDF: {e}")
        return None

def update_boletim_file(boletim_info):
    """
    Atualiza o arquivo boletim.json e faz o download do PDF
    """
    try:
        # Criar diretório se não existir
        os.makedirs("files", exist_ok=True)
        
        # Fazer download do PDF
        pdf_path = download_pdf(boletim_info["redirect"])
        
        if not pdf_path:
            logging.warning("Erro ao baixar o arquivo PDF do boletim")
            return False
        
        # Estrutura do arquivo JSON
        boletim_data = {
            "boletimDate": boletim_info["date_str"],
            "link": boletim_info["redirect"],
            "updatedAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Salvar no arquivo JSON
        json_file_path = "files/boletim_info.json"
        create_json(boletim_data, json_file_path)
        
        logging.info(f"Boletim atualizado com sucesso! Data: {boletim_info['date_str']}")
        return True
        
    except Exception as e:
        logging.info(f"Erro ao atualizar arquivo do boletim: {e}")
        return False
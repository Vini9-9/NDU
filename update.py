import main
import utils
import zero
import playoff
from colorama import Fore, Style

dic_modalities_page = utils.get_current_dic_modalities_page()

def menu():
    
    utils.print_colored("O que deseja atualizar?", Fore.YELLOW)
    utils.print_colored("G - Tudo da fase de grupos")
    utils.print_colored("J - Apenas Jogos")
    utils.print_colored("P - Tudo do playoff")
    utils.print_colored("R - Ranking por modalidade")
    utils.print_colored("Z - do zero")
    
    choice = input(Fore.GREEN + "Escolha uma opção: " + Style.RESET_ALL).capitalize()
    
    if choice == "G":
        update_all_group()
    elif choice == "R":
        update_ranking_by_modality()
    elif choice == "J":
        update_games()
    elif choice == "P":
        update_playoff()
    elif choice == "Z":
        update_data_from_zero()
    else:
        print("Opção inválida.")

def update_all_group():
    utils.print_magenta("Atualizando tudo...")
    main.execute_update_data(dic_modalities_page)

def update_data_from_zero():
    utils.print_magenta("Atualizando do zero...")
    zero.execute_zero_ranking(dic_modalities_page)

def update_ranking_by_modality():
    modality = input(Fore.GREEN + "Informe a modalidade (ex: FM/A): " + Style.RESET_ALL)
    utils.print_magenta(f"Atualizando ranking para a modalidade {modality}...")
    main.update_ranking_by_games(modality)

def update_playoff():
    playoff.execute_update_data_playoff(dic_modalities_page)
    # modality = input(Fore.GREEN + "Informe a modalidade (ex: FM/A): " + Style.RESET_ALL)
    # if modality:
    #     print_magenta(f"Atualizando playoff para a modalidade {modality}...")
    #     playoff.execute_update_data_playoff_by_modality(modality)
    # else:
    #   playoff.execute_update_data_playoff(dic_modalities_page)

def update_games():
    utils.print_magenta("Atualizando apenas jogos...")
    main.execute_update_games(dic_modalities_page)

if __name__ == "__main__":
    menu()
#Bibliotecas
#Tkinter para criar o visual | Threading para executar em segundo plano | subprocess para executar em segundo plano o CMD
#Datetime para capturar datas e horas
import tkinter as tk
import time, threading, subprocess, datetime, os
import win32com.client as win32
import pythoncom


#Cores
azul = "#282A36"
azul_botao = "#5067AA"
azul_claro = "#343746"
branco = "#FFFFFF"
cinza = "#F5F5F5"
preto = "#000000"
preto_end = "#0F0F0F"
preto_front = "#282827"
verde = "#00BC8C"
vermelho = "#E74C3C"


#Variaveis Globais
#define o status como True ou False, fazendo com que inicie ou pare uma function
status = True
dispositivo = ""
erro_apresentado = ""
ip_monitorado = ""
enviar_email = 0
pasta_log = "" #Digite entre "" o caminho para a pasta onde deseja guardar o log


#DEFs
def MandarEmail():
    global dispositivo, erro_apresentado, ip_monitorado, enviar_email
    if enviar_email == 1:
        try:
            # Inicializa o COM para este thread
            pythoncom.CoInitialize()  
            #criar a integração com o outlook
            outlook = win32.Dispatch('outlook.application')
            #criar um email
            email = outlook.CreateItem(0)
            #configurar as informações do seu e-mail
            email.To = "" #Digite entre "" os emails que deseja que recebam os alertas
            email.Subject = "Erro com dispositivo monitorado"
            email.HTMLBody = f"""
            <p>Algo aconteceu com o dispositivo {dispositivo}, enquanto ele estava sendo monitorado via Ping</p>

            <p>IP de monitoramento: {ip_monitorado}</p>

            <p>Erro apresentado: {erro_apresentado}</p>

            <p>Atenciosamente,</p>
            <p>TI IPA</p>
            
            <p></p>
            """
            #anexo = ""
            #email.Attachments.Add(anexo)
            #Envia o email e espera 10 segundos para enviar o proximo 
            email.Send()
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
        finally:
            # Libera recursos COM no final
            pythoncom.CoUninitialize() 
    else:
        pass 

def pingar():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 0
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_1.configure(state="disabled")
    FrameCima.entry_monitora_1_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_1.get() =="") or (FrameCima.entry_monitora_1.get() ==" "):
        FrameCima.frame_monitora_1.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_1_2.get() =="") or (FrameCima.entry_monitora_1_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_1_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        mandar = 1
                        FrameCima.texto_monitora_1.configure(bg=vermelho)
                        FrameCima.frame_monitora_1.configure(bg=vermelho)
                        FrameCima.frame_monitora_1_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_1_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(2)
                        dispositivo = FrameCima.entry_monitora_1.get()
                        ip_monitorado = FrameCima.entry_monitora_1_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1 
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        mandar = 1
                        FrameCima.texto_monitora_1.configure(bg=vermelho)
                        FrameCima.frame_monitora_1.configure(bg=vermelho)
                        FrameCima.frame_monitora_1_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_1_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(2)
                        dispositivo = FrameCima.entry_monitora_1.get()
                        ip_monitorado = FrameCima.entry_monitora_1_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1 
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        enviar_email = 0
                        mandar = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_1.configure(bg=verde)
                        FrameCima.frame_monitora_1.configure(bg=verde)
                        FrameCima.frame_monitora_1_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    mandar = 1
                    FrameCima.texto_monitora_1.configure(bg=vermelho)
                    FrameCima.frame_monitora_1.configure(bg=vermelho)
                    FrameCima.frame_monitora_1_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_1_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(2)
                    dispositivo = FrameCima.entry_monitora_1.get()
                    ip_monitorado = FrameCima.entry_monitora_1_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1 
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar2():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_2.configure(state="disabled")
    FrameCima.entry_monitora_2_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_2.get() =="") or (FrameCima.entry_monitora_2.get() ==" "):
        FrameCima.frame_monitora_2.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_2_2.get() =="") or (FrameCima.entry_monitora_2_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_2_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_2.configure(bg=vermelho)
                        FrameCima.frame_monitora_2.configure(bg=vermelho)
                        FrameCima.frame_monitora_2_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_2_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(4)
                        dispositivo = FrameCima.entry_monitora_2.get()
                        ip_monitorado = FrameCima.entry_monitora_2_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_2.configure(bg=vermelho)
                        FrameCima.frame_monitora_2.configure(bg=vermelho)
                        FrameCima.frame_monitora_2_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_2_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(4)
                        dispositivo = FrameCima.entry_monitora_2.get()
                        ip_monitorado = FrameCima.entry_monitora_2_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_2.configure(bg=verde)
                        FrameCima.frame_monitora_2.configure(bg=verde)
                        FrameCima.frame_monitora_2_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_2.configure(bg=vermelho)
                    FrameCima.frame_monitora_2.configure(bg=vermelho)
                    FrameCima.frame_monitora_2_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_2_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(4)
                    dispositivo = FrameCima.entry_monitora_2.get()
                    ip_monitorado = FrameCima.entry_monitora_2_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar3():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_3.configure(state="disabled")
    FrameCima.entry_monitora_3_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_3.get() =="") or (FrameCima.entry_monitora_3.get() ==" "):
        FrameCima.frame_monitora_3.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_3_2.get() =="") or (FrameCima.entry_monitora_3_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_3_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_3.configure(bg=vermelho)
                        FrameCima.frame_monitora_3.configure(bg=vermelho)
                        FrameCima.frame_monitora_3_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_3_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(6)
                        dispositivo = FrameCima.entry_monitora_3.get()
                        ip_monitorado = FrameCima.entry_monitora_3_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_3.configure(bg=vermelho)
                        FrameCima.frame_monitora_3.configure(bg=vermelho)
                        FrameCima.frame_monitora_3_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_3_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(6)
                        dispositivo = FrameCima.entry_monitora_3.get()
                        ip_monitorado = FrameCima.entry_monitora_3_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_3.configure(bg=verde)
                        FrameCima.frame_monitora_3.configure(bg=verde)
                        FrameCima.frame_monitora_3_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_3.configure(bg=vermelho)
                    FrameCima.frame_monitora_3.configure(bg=vermelho)
                    FrameCima.frame_monitora_3_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_3_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(6)
                    dispositivo = FrameCima.entry_monitora_3.get()
                    ip_monitorado = FrameCima.entry_monitora_3_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar4():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_4.configure(state="disabled")
    FrameCima.entry_monitora_4_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_4.get() =="") or (FrameCima.entry_monitora_4.get() ==" "):
        FrameCima.frame_monitora_4.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_4_2.get() =="") or (FrameCima.entry_monitora_4_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_4_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_4.configure(bg=vermelho)
                        FrameCima.frame_monitora_4.configure(bg=vermelho)
                        FrameCima.frame_monitora_4_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_4_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(8)
                        dispositivo = FrameCima.entry_monitora_4.get()
                        ip_monitorado = FrameCima.entry_monitora_4_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_4.configure(bg=vermelho)
                        FrameCima.frame_monitora_4.configure(bg=vermelho)
                        FrameCima.frame_monitora_4_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_4_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(8)
                        dispositivo = FrameCima.entry_monitora_4.get()
                        ip_monitorado = FrameCima.entry_monitora_4_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_4.configure(bg=verde)
                        FrameCima.frame_monitora_4.configure(bg=verde)
                        FrameCima.frame_monitora_4_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_4.configure(bg=vermelho)
                    FrameCima.frame_monitora_4.configure(bg=vermelho)
                    FrameCima.frame_monitora_4_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_4_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(8)
                    dispositivo = FrameCima.entry_monitora_4.get()
                    ip_monitorado = FrameCima.entry_monitora_4_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar5():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_5.configure(state="disabled")
    FrameCima.entry_monitora_5_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_5.get() =="") or (FrameCima.entry_monitora_5.get() ==" "):
        FrameCima.frame_monitora_5.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_5_2.get() =="") or (FrameCima.entry_monitora_5_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_5_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_5.configure(bg=vermelho)
                        FrameCima.frame_monitora_5.configure(bg=vermelho)
                        FrameCima.frame_monitora_5_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_5_2.get()} Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(10)
                        dispositivo = FrameCima.entry_monitora_5.get()
                        ip_monitorado = FrameCima.entry_monitora_5_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_5.configure(bg=vermelho)
                        FrameCima.frame_monitora_5.configure(bg=vermelho)
                        FrameCima.frame_monitora_5_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_5_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(10)
                        dispositivo = FrameCima.entry_monitora_5.get()
                        ip_monitorado = FrameCima.entry_monitora_5_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_5.configure(bg=verde)
                        FrameCima.frame_monitora_5.configure(bg=verde)
                        FrameCima.frame_monitora_5_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_5.configure(bg=vermelho)
                    FrameCima.frame_monitora_5.configure(bg=vermelho)
                    FrameCima.frame_monitora_5_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_5_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(10)
                    dispositivo = FrameCima.entry_monitora_5.get()
                    ip_monitorado = FrameCima.entry_monitora_5_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar6():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_6.configure(state="disabled")
    FrameCima.entry_monitora_6_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_6.get() =="") or (FrameCima.entry_monitora_6.get() ==" "):
        FrameCima.frame_monitora_6.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_6_2.get() =="") or (FrameCima.entry_monitora_6_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_6_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_6.configure(bg=vermelho)
                        FrameCima.frame_monitora_6.configure(bg=vermelho)
                        FrameCima.frame_monitora_6_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_6_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(12)
                        dispositivo = FrameCima.entry_monitora_6.get()
                        ip_monitorado = FrameCima.entry_monitora_6_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_6.configure(bg=vermelho)
                        FrameCima.frame_monitora_6.configure(bg=vermelho)
                        FrameCima.frame_monitora_6_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_6_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(12)
                        dispositivo = FrameCima.entry_monitora_6.get()
                        ip_monitorado = FrameCima.entry_monitora_6_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_6.configure(bg=verde)
                        FrameCima.frame_monitora_6.configure(bg=verde)
                        FrameCima.frame_monitora_6_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_6.configure(bg=vermelho)
                    FrameCima.frame_monitora_6.configure(bg=vermelho)
                    FrameCima.frame_monitora_6_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_6_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(12)
                    dispositivo = FrameCima.entry_monitora_6.get()
                    ip_monitorado = FrameCima.entry_monitora_6_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar7():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_7.configure(state="disabled")
    FrameCima.entry_monitora_7_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_7.get() =="") or (FrameCima.entry_monitora_7.get() ==" "):
        FrameCima.frame_monitora_7.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_7_2.get() =="") or (FrameCima.entry_monitora_7_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_7_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_7.configure(bg=vermelho)
                        FrameCima.frame_monitora_7.configure(bg=vermelho)
                        FrameCima.frame_monitora_7_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_7_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(14)
                        dispositivo = FrameCima.entry_monitora_7.get()
                        ip_monitorado = FrameCima.entry_monitora_7_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_7.configure(bg=vermelho)
                        FrameCima.frame_monitora_7.configure(bg=vermelho)
                        FrameCima.frame_monitora_7_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_7_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(14)
                        dispositivo = FrameCima.entry_monitora_7.get()
                        ip_monitorado = FrameCima.entry_monitora_7_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_7.configure(bg=verde)
                        FrameCima.frame_monitora_7.configure(bg=verde)
                        FrameCima.frame_monitora_7_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_7.configure(bg=vermelho)
                    FrameCima.frame_monitora_7.configure(bg=vermelho)
                    FrameCima.frame_monitora_7_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_7_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(14)
                    dispositivo = FrameCima.entry_monitora_7.get()
                    ip_monitorado = FrameCima.entry_monitora_7_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar8():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_8.configure(state="disabled")
    FrameCima.entry_monitora_8_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_8.get() =="") or (FrameCima.entry_monitora_8.get() ==" "):
        FrameCima.frame_monitora_8.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_8_2.get() =="") or (FrameCima.entry_monitora_8_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_8_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_8.configure(bg=vermelho)
                        FrameCima.frame_monitora_8.configure(bg=vermelho)
                        FrameCima.frame_monitora_8_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_8_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(16)
                        dispositivo = FrameCima.entry_monitora_8.get()
                        ip_monitorado = FrameCima.entry_monitora_8_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_8.configure(bg=vermelho)
                        FrameCima.frame_monitora_8.configure(bg=vermelho)
                        FrameCima.frame_monitora_8_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_8_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(16)
                        dispositivo = FrameCima.entry_monitora_8.get()
                        ip_monitorado = FrameCima.entry_monitora_8_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_8.configure(bg=verde)
                        FrameCima.frame_monitora_8.configure(bg=verde)
                        FrameCima.frame_monitora_8_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_8.configure(bg=vermelho)
                    FrameCima.frame_monitora_8.configure(bg=vermelho)
                    FrameCima.frame_monitora_8_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_8_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(16)
                    dispositivo = FrameCima.entry_monitora_8.get()
                    ip_monitorado = FrameCima.entry_monitora_8_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar9():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_9.configure(state="disabled")
    FrameCima.entry_monitora_9_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_9.get() =="") or (FrameCima.entry_monitora_9.get() ==" "):
        FrameCima.frame_monitora_9.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_9_2.get() =="") or (FrameCima.entry_monitora_9_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_9_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_9.configure(bg=vermelho)
                        FrameCima.frame_monitora_9.configure(bg=vermelho)
                        FrameCima.frame_monitora_9_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_9_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(18)
                        dispositivo = FrameCima.entry_monitora_9.get()
                        ip_monitorado = FrameCima.entry_monitora_9_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_9.configure(bg=vermelho)
                        FrameCima.frame_monitora_9.configure(bg=vermelho)
                        FrameCima.frame_monitora_9_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_9_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(18)
                        dispositivo = FrameCima.entry_monitora_9.get()
                        ip_monitorado = FrameCima.entry_monitora_9_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_9.configure(bg=verde)
                        FrameCima.frame_monitora_9.configure(bg=verde)
                        FrameCima.frame_monitora_9_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_9.configure(bg=vermelho)
                    FrameCima.frame_monitora_9.configure(bg=vermelho)
                    FrameCima.frame_monitora_9_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_9_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(18)
                    dispositivo = FrameCima.entry_monitora_9.get()
                    ip_monitorado = FrameCima.entry_monitora_9_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar10():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_10.configure(state="disabled")
    FrameCima.entry_monitora_10_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_10.get() =="") or (FrameCima.entry_monitora_10.get() ==" "):
        FrameCima.frame_monitora_10.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_10_2.get() =="") or (FrameCima.entry_monitora_10_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_10_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_10.configure(bg=vermelho)
                        FrameCima.frame_monitora_10.configure(bg=vermelho)
                        FrameCima.frame_monitora_10_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_10_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(20)
                        dispositivo = FrameCima.entry_monitora_10.get()
                        ip_monitorado = FrameCima.entry_monitora_10_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_10.configure(bg=vermelho)
                        FrameCima.frame_monitora_10.configure(bg=vermelho)
                        FrameCima.frame_monitora_10_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_10_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(20)
                        dispositivo = FrameCima.entry_monitora_10.get()
                        ip_monitorado = FrameCima.entry_monitora_10_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_10.configure(bg=verde)
                        FrameCima.frame_monitora_10.configure(bg=verde)
                        FrameCima.frame_monitora_10_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_10.configure(bg=vermelho)
                    FrameCima.frame_monitora_10.configure(bg=vermelho)
                    FrameCima.frame_monitora_10_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_10_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(20)
                    dispositivo = FrameCima.entry_monitora_10.get()
                    ip_monitorado = FrameCima.entry_monitora_10_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar11():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_11.configure(state="disabled")
    FrameCima.entry_monitora_11_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_11.get() =="") or (FrameCima.entry_monitora_11.get() ==" "):
        FrameCima.frame_monitora_11.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_11_2.get() =="") or (FrameCima.entry_monitora_11_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_11_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_11.configure(bg=vermelho)
                        FrameCima.frame_monitora_11.configure(bg=vermelho)
                        FrameCima.frame_monitora_11_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_11_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(22)
                        dispositivo = FrameCima.entry_monitora_11.get()
                        ip_monitorado = FrameCima.entry_monitora_11_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_11.configure(bg=vermelho)
                        FrameCima.frame_monitora_11.configure(bg=vermelho)
                        FrameCima.frame_monitora_11_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_11_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(22)
                        dispositivo = FrameCima.entry_monitora_11.get()
                        ip_monitorado = FrameCima.entry_monitora_11_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_11.configure(bg=verde)
                        FrameCima.frame_monitora_11.configure(bg=verde)
                        FrameCima.frame_monitora_11_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_11.configure(bg=vermelho)
                    FrameCima.frame_monitora_11.configure(bg=vermelho)
                    FrameCima.frame_monitora_11_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_11_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(22)
                    dispositivo = FrameCima.entry_monitora_11.get()
                    ip_monitorado = FrameCima.entry_monitora_11_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar12():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_12.configure(state="disabled")
    FrameCima.entry_monitora_12_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_12.get() =="") or (FrameCima.entry_monitora_12.get() ==" "):
        FrameCima.frame_monitora_12.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_12_2.get() =="") or (FrameCima.entry_monitora_12_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_12_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_12.configure(bg=vermelho)
                        FrameCima.frame_monitora_12.configure(bg=vermelho)
                        FrameCima.frame_monitora_12_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_12_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(24)
                        dispositivo = FrameCima.entry_monitora_12.get()
                        ip_monitorado = FrameCima.entry_monitora_12_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_12.configure(bg=vermelho)
                        FrameCima.frame_monitora_12.configure(bg=vermelho)
                        FrameCima.frame_monitora_12_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_12_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(24)
                        dispositivo = FrameCima.entry_monitora_12.get()
                        ip_monitorado = FrameCima.entry_monitora_12_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_12.configure(bg=verde)
                        FrameCima.frame_monitora_12.configure(bg=verde)
                        FrameCima.frame_monitora_12_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_12.configure(bg=vermelho)
                    FrameCima.frame_monitora_12.configure(bg=vermelho)
                    FrameCima.frame_monitora_12_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_12_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(24)
                    dispositivo = FrameCima.entry_monitora_12.get()
                    ip_monitorado = FrameCima.entry_monitora_12_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar13():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_13.configure(state="disabled")
    FrameCima.entry_monitora_13_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_13.get() =="") or (FrameCima.entry_monitora_13.get() ==" "):
        FrameCima.frame_monitora_13.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_13_2.get() =="") or (FrameCima.entry_monitora_13_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_13_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_13.configure(bg=vermelho)
                        FrameCima.frame_monitora_13.configure(bg=vermelho)
                        FrameCima.frame_monitora_13_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_13_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(26)
                        dispositivo = FrameCima.entry_monitora_13.get()
                        ip_monitorado = FrameCima.entry_monitora_13_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_13.configure(bg=vermelho)
                        FrameCima.frame_monitora_13.configure(bg=vermelho)
                        FrameCima.frame_monitora_13_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_13_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(26)
                        dispositivo = FrameCima.entry_monitora_13.get()
                        ip_monitorado = FrameCima.entry_monitora_13_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_13.configure(bg=verde)
                        FrameCima.frame_monitora_13.configure(bg=verde)
                        FrameCima.frame_monitora_13_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_13.configure(bg=vermelho)
                    FrameCima.frame_monitora_13.configure(bg=vermelho)
                    FrameCima.frame_monitora_13_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_13_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(26)
                    dispositivo = FrameCima.entry_monitora_13.get()
                    ip_monitorado = FrameCima.entry_monitora_13_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar14():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_14.configure(state="disabled")
    FrameCima.entry_monitora_14_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_14.get() =="") or (FrameCima.entry_monitora_14.get() ==" "):
        FrameCima.frame_monitora_14.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_14_2.get() =="") or (FrameCima.entry_monitora_14_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_14_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_14.configure(bg=vermelho)
                        FrameCima.frame_monitora_14.configure(bg=vermelho)
                        FrameCima.frame_monitora_14_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_14_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(28)
                        dispositivo = FrameCima.entry_monitora_14.get()
                        ip_monitorado = FrameCima.entry_monitora_14_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_14.configure(bg=vermelho)
                        FrameCima.frame_monitora_14.configure(bg=vermelho)
                        FrameCima.frame_monitora_14_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_14_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(28)
                        dispositivo = FrameCima.entry_monitora_14.get()
                        ip_monitorado = FrameCima.entry_monitora_14_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_14.configure(bg=verde)
                        FrameCima.frame_monitora_14.configure(bg=verde)
                        FrameCima.frame_monitora_14_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_14.configure(bg=vermelho)
                    FrameCima.frame_monitora_14.configure(bg=vermelho)
                    FrameCima.frame_monitora_14_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_14_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(28)
                    dispositivo = FrameCima.entry_monitora_14.get()
                    ip_monitorado = FrameCima.entry_monitora_14_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar15():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_15.configure(state="disabled")
    FrameCima.entry_monitora_15_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_15.get() =="") or (FrameCima.entry_monitora_15.get() ==" "):
        FrameCima.frame_monitora_15.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_15_2.get() =="") or (FrameCima.entry_monitora_15_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_15_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_15.configure(bg=vermelho)
                        FrameCima.frame_monitora_15.configure(bg=vermelho)
                        FrameCima.frame_monitora_15_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_15_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(30)
                        dispositivo = FrameCima.entry_monitora_15.get()
                        ip_monitorado = FrameCima.entry_monitora_15_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_15.configure(bg=vermelho)
                        FrameCima.frame_monitora_15.configure(bg=vermelho)
                        FrameCima.frame_monitora_15_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_15_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(30)
                        dispositivo = FrameCima.entry_monitora_15.get()
                        ip_monitorado = FrameCima.entry_monitora_15_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_15.configure(bg=verde)
                        FrameCima.frame_monitora_15.configure(bg=verde)
                        FrameCima.frame_monitora_15_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_15.configure(bg=vermelho)
                    FrameCima.frame_monitora_15.configure(bg=vermelho)
                    FrameCima.frame_monitora_15_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_15_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(30)
                    dispositivo = FrameCima.entry_monitora_15.get()
                    ip_monitorado = FrameCima.entry_monitora_15_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def pingar16():
    #Chamando variavel global e definindo ela como True
    global status, dispositivo, erro_apresentado, ip_monitorado, enviar_email, pasta_log
    status = True
    #variavel interna 
    mandar = 1
    #Travando a edição nos campos de texto e de ip
    FrameCima.entry_monitora_16.configure(state="disabled")
    FrameCima.entry_monitora_16_2.configure(state="disabled")
    #Verificando se o campo Equipamento esta vazio, se tiver, ele coloca o frame como disable e tira ele visualmente
    if (FrameCima.entry_monitora_16.get() =="") or (FrameCima.entry_monitora_16.get() ==" "):
        FrameCima.frame_monitora_16.place_forget()    
    else:
        #Verificando se o campo ip esta vazio, se tiver, ignora e não deixa travar o codigo
        if (FrameCima.entry_monitora_16_2.get() =="") or (FrameCima.entry_monitora_16_2.get() == " "):
            pass
        #Verificando se o campo de ip tem alguma informação, se tiver, começa a executar o looping enquanto a variavel status for True
        else:
            while status:
                #Tratando as possiveis respostas que o CMD pode retornar e configurando as cores do infos_monitora
                try:
                    data_hora_atualizada = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    saida_cmd = subprocess.check_output(['ping', FrameCima.entry_monitora_16_2.get()], text=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                    #O host de destino não pode ser alcançado pela rede, configura infos_monitora como vermelho e imprime o erro
                    if "Host de destino inacessivel" in saida_cmd:
                        FrameCima.texto_monitora_16.configure(bg=vermelho)
                        FrameCima.frame_monitora_16.configure(bg=vermelho)
                        FrameCima.frame_monitora_16_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_16_2.get()} - Host de destino inacessivel para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(32)
                        dispositivo = FrameCima.entry_monitora_16.get()
                        ip_monitorado = FrameCima.entry_monitora_16_2.get()
                        erro_apresentado = "Host de destino inacessivel"
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #O host de destino não respondeu ao ping dentro do tempo limite definido, configura infos_monitora como vermelho e imprime o erro
                    elif  "Esgotado o tempo limite do pedido." in saida_cmd:
                        FrameCima.texto_monitora_16.configure(bg=vermelho)
                        FrameCima.frame_monitora_16.configure(bg=vermelho)
                        FrameCima.frame_monitora_16_2.configure(bg=vermelho)
                        #Preenche o arquivo txt com as informações do erro
                        log = open(pasta_log, "a")
                        log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_16_2.get()} - Esgotado o tempo limite do pedido para o IP\n")
                        log.close()
                        #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                        time.sleep(32)
                        dispositivo = FrameCima.entry_monitora_16.get()
                        ip_monitorado = FrameCima.entry_monitora_16_2.get()
                        erro_apresentado = "Esgotado o tempo limite do pedido."
                        #Se a variavel for 1, manda o email, se for 0, não manda
                        if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                        else:
                            pass
                    #Caso não retorne algum desses erros, configura infos_monitora como verde
                    else:
                        mandar = 1
                        enviar_email = 0
                        #Configura os campos para verde, sinalizando que esta tudo ok
                        FrameCima.texto_monitora_16.configure(bg=verde)
                        FrameCima.frame_monitora_16.configure(bg=verde)
                        FrameCima.frame_monitora_16_2.configure(bg=verde)
                #Se a tentativa de pingar de algum outro erro fora esses ja tratados, configura infos_monitora como vermelho e imprime o erro
                except subprocess.CalledProcessError as erro_processo_cmd:
                    FrameCima.texto_monitora_16.configure(bg=vermelho)
                    FrameCima.frame_monitora_16.configure(bg=vermelho)
                    FrameCima.frame_monitora_16_2.configure(bg=vermelho)
                    #Preenche o arquivo txt com as informações do erro
                    log = open(pasta_log, "a")
                    log.write(f"{data_hora_atualizada} - IP: {FrameCima.entry_monitora_16_2.get()} - {erro_processo_cmd}\n")
                    log.close()
                    #Espera alguns segundos (a cada def aumenta 2 segundos) e manda as informações do erro para a def MandarEmail
                    time.sleep(32)
                    dispositivo = FrameCima.entry_monitora_16.get()
                    ip_monitorado = FrameCima.entry_monitora_16_2.get()
                    erro_apresentado = f"{erro_processo_cmd}"
                    #Se a variavel for 1, manda o email, se for 0, não manda
                    if mandar == 1:
                            enviar_email += 1
                            MandarEmail()
                            mandar = 0
                    else:
                        pass

def PausarPing():
    #Chamando variavel global e definindo ela como False
    global status
    status = False
    #Espera 5 segundos e configura infos_monitora como branco
    time.sleep(5)
    #Cria uma lista vazia que vai ser preenchida com as informações do primeiro loop
    entries = []
    for i in range(1, 17):
        frame = f"frame_monitora_{i}"
        texto = f"texto_monitora_{i}"
        entries.append(getattr(FrameCima, texto))
        entries.append(getattr(FrameCima, frame))
        entries.append(getattr(FrameCima, f"{frame}_2"))
    #Busca as informações na lista e troca as infos_monitora e texto_monitora para branco
    for i in entries:
        i.configure(bg=azul_botao)

def Pausar():
    #Chamando variavel global e definindo ela como False
    global status
    status = False
    #Troca o texto para "iniciar" e configura o comando para chamar o iniciar novamente
    FrameBaixo.bt1.configure(text="Iniciar", font=("Arial", 10, "bold"), command=Iniciar)
    #Configura e chama o executvel "PararPing"
    pausar_segundo_plano = threading.Thread(target = PausarPing)
    pausar_segundo_plano.daemon = True
    pausar_segundo_plano.start()
    #Cria uma lista com as posições de cada frame que vamos utilizar
    lugares = [(15, 40), (310, 40), (15, 100), (310, 100), (15, 160), (310, 160), (15, 220), (310, 220),
                 (15, 280), (310, 280), (15, 340), (310, 340), (15, 400), (310, 400), (15, 460), (310, 460)]
    #Roda o loop até acabar as informações da lista, vai executar 16 vezes e colocar os campos nos lugares
    for i, lugares in enumerate(lugares, start=1):
        getattr(FrameCima, f"frame_monitora_{i}").place(x=lugares[0], y=lugares[1])
    #Cria uma lista vazia que vai ser preenchida com as informações do primeiro loop
    entries = []
    for i in range(1, 17):
        nome_entry = f"entry_monitora_{i}"
        entries.append(getattr(FrameCima, nome_entry))
        entries.append(getattr(FrameCima, f"{nome_entry}_2"))
    #Busca as informações na lista e configura os campos de texto e ip para normal, permitindo edição novamente    
    for i in entries:
        i.configure(state="normal")

def Iniciar():
    #Configura e chama o executvel "Pingar"
    pingar_segundo_plano_1 = threading.Thread(target = pingar)
    pingar_segundo_plano_2 = threading.Thread(target = pingar2)
    pingar_segundo_plano_3 = threading.Thread(target = pingar3)
    pingar_segundo_plano_4 = threading.Thread(target = pingar4)
    pingar_segundo_plano_5 = threading.Thread(target = pingar5)
    pingar_segundo_plano_6 = threading.Thread(target = pingar6)
    pingar_segundo_plano_7 = threading.Thread(target = pingar7)
    pingar_segundo_plano_8 = threading.Thread(target = pingar8)
    pingar_segundo_plano_9 = threading.Thread(target = pingar9)
    pingar_segundo_plano_10 = threading.Thread(target = pingar10)
    pingar_segundo_plano_11 = threading.Thread(target = pingar11)
    pingar_segundo_plano_12 = threading.Thread(target = pingar12)
    pingar_segundo_plano_13 = threading.Thread(target = pingar13)
    pingar_segundo_plano_14 = threading.Thread(target = pingar14)
    pingar_segundo_plano_15 = threading.Thread(target = pingar15)
    pingar_segundo_plano_16 = threading.Thread(target = pingar16)
    #Define o daemon como verdadeiro para executar
    pingar_segundo_plano_1.daemon = True
    pingar_segundo_plano_2.daemon = True
    pingar_segundo_plano_3.daemon = True
    pingar_segundo_plano_4.daemon = True
    pingar_segundo_plano_5.daemon = True
    pingar_segundo_plano_6.daemon = True
    pingar_segundo_plano_7.daemon = True
    pingar_segundo_plano_8.daemon = True
    pingar_segundo_plano_9.daemon = True
    pingar_segundo_plano_10.daemon = True
    pingar_segundo_plano_11.daemon = True
    pingar_segundo_plano_12.daemon = True
    pingar_segundo_plano_13.daemon = True
    pingar_segundo_plano_14.daemon = True
    pingar_segundo_plano_15.daemon = True
    pingar_segundo_plano_16.daemon = True
    #Inicia a execução
    pingar_segundo_plano_1.start()
    pingar_segundo_plano_2.start()
    pingar_segundo_plano_3.start()
    pingar_segundo_plano_4.start()
    pingar_segundo_plano_5.start()
    pingar_segundo_plano_6.start()
    pingar_segundo_plano_7.start()
    pingar_segundo_plano_8.start()
    pingar_segundo_plano_9.start()
    pingar_segundo_plano_10.start()
    pingar_segundo_plano_11.start()
    pingar_segundo_plano_12.start()
    pingar_segundo_plano_13.start()
    pingar_segundo_plano_14.start()
    pingar_segundo_plano_15.start()
    pingar_segundo_plano_16.start()
    #Troca o texto para "Pausar" e configura o comando para chamar o Pausar novamente
    FrameBaixo.bt1.configure(text="Pausar", font=("Arial", 10, "bold"), command=Pausar)    

def GerarLog():
    global pasta_log
    os.startfile(pasta_log)


#configuração principal
monitor = tk.Tk()
monitor.title('Monitoramento por IP')
monitor.geometry('600x550')
monitor.resizable(False, False)
monitor.iconbitmap("image/ip.ico")


class FrameCima:
    #Configuração do frame da parte de cima
    frame_cima = tk.Frame(monitor, width=600, height=522, bg=cinza, relief="flat")
    frame_cima.place(x=0, y=0)

    #Texto na parte superior
    text = tk.Label(frame_cima, text="Monitoramento por IP", font=("Arial", 18, "bold"), 
                    bg= cinza, fg=azul_botao)
    text.place(x=150, y=2)

    #Layout para o campo de texto e ip 

    frame_monitora_1 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_1.place(x=15, y=40)
    texto_monitora_1 = tk.Label(frame_monitora_1, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_1.place(x=0, y=0)
    entry_monitora_1 = tk.Entry(frame_monitora_1, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_1.place(x=87, y=1)
    frame_monitora_1_2 = tk.Label(frame_monitora_1, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_1_2.place(x=5, y=22)
    entry_monitora_1_2 = tk.Entry(frame_monitora_1, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_1_2.place(x=87, y=23)

    frame_monitora_2 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_2.place(x=310, y=40)
    texto_monitora_2 = tk.Label(frame_monitora_2, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_2.place(x=0, y=0)
    entry_monitora_2 = tk.Entry(frame_monitora_2, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_2.place(x=87, y=1)
    frame_monitora_2_2 = tk.Label(frame_monitora_2, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_2_2.place(x=5, y=22)
    entry_monitora_2_2 = tk.Entry(frame_monitora_2, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_2_2.place(x=87, y=23)

    frame_monitora_3 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_3.place(x=15, y=100)
    texto_monitora_3 = tk.Label(frame_monitora_3, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_3.place(x=0, y=0)
    entry_monitora_3 = tk.Entry(frame_monitora_3, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_3.place(x=87, y=1)
    frame_monitora_3_2 = tk.Label(frame_monitora_3, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_3_2.place(x=5, y=22)
    entry_monitora_3_2 = tk.Entry(frame_monitora_3, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_3_2.place(x=87, y=23)

    frame_monitora_4 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_4.place(x=310, y=100)
    texto_monitora_4 = tk.Label(frame_monitora_4, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_4.place(x=0, y=0)
    entry_monitora_4 = tk.Entry(frame_monitora_4, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_4.place(x=87, y=1)
    frame_monitora_4_2 = tk.Label(frame_monitora_4, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_4_2.place(x=5, y=22)
    entry_monitora_4_2 = tk.Entry(frame_monitora_4, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_4_2.place(x=87, y=23)

    frame_monitora_5 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_5.place(x=15, y=160)
    texto_monitora_5 = tk.Label(frame_monitora_5, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_5.place(x=0, y=0)
    entry_monitora_5 = tk.Entry(frame_monitora_5, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_5.place(x=87, y=1)
    frame_monitora_5_2 = tk.Label(frame_monitora_5, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_5_2.place(x=5, y=22)
    entry_monitora_5_2 = tk.Entry(frame_monitora_5, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_5_2.place(x=87, y=23)

    frame_monitora_6 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_6.place(x=310, y=160)
    texto_monitora_6 = tk.Label(frame_monitora_6, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_6.place(x=0, y=0)
    entry_monitora_6 = tk.Entry(frame_monitora_6, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_6.place(x=87, y=1)
    frame_monitora_6_2 = tk.Label(frame_monitora_6, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_6_2.place(x=5, y=22)
    entry_monitora_6_2 = tk.Entry(frame_monitora_6, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_6_2.place(x=87, y=23)

    frame_monitora_7 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_7.place(x=15, y=220)
    texto_monitora_7 = tk.Label(frame_monitora_7, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_7.place(x=0, y=0)
    entry_monitora_7 = tk.Entry(frame_monitora_7, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_7.place(x=87, y=1)
    frame_monitora_7_2 = tk.Label(frame_monitora_7, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_7_2.place(x=5, y=22)
    entry_monitora_7_2 = tk.Entry(frame_monitora_7, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_7_2.place(x=87, y=23)

    frame_monitora_8 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_8.place(x=310, y=220)
    texto_monitora_8 = tk.Label(frame_monitora_8, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_8.place(x=0, y=0)
    entry_monitora_8 = tk.Entry(frame_monitora_8, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_8.place(x=87, y=1)
    frame_monitora_8_2 = tk.Label(frame_monitora_8, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_8_2.place(x=5, y=22)
    entry_monitora_8_2 = tk.Entry(frame_monitora_8, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_8_2.place(x=87, y=23)

    frame_monitora_9 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_9.place(x=15, y=280)
    texto_monitora_9 = tk.Label(frame_monitora_9, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_9.place(x=0, y=0)
    entry_monitora_9 = tk.Entry(frame_monitora_9, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_9.place(x=87, y=1)
    frame_monitora_9_2 = tk.Label(frame_monitora_9, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_9_2.place(x=5, y=22)
    entry_monitora_9_2 = tk.Entry(frame_monitora_9, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_9_2.place(x=87, y=23)

    frame_monitora_10 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_10.place(x=310, y=280)
    texto_monitora_10 = tk.Label(frame_monitora_10, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_10.place(x=0, y=0)
    entry_monitora_10 = tk.Entry(frame_monitora_10, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_10.place(x=87, y=1)
    frame_monitora_10_2 = tk.Label(frame_monitora_10, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_10_2.place(x=5, y=22)
    entry_monitora_10_2 = tk.Entry(frame_monitora_10, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_10_2.place(x=87, y=23)

    frame_monitora_11 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_11.place(x=15, y=340)
    texto_monitora_11 = tk.Label(frame_monitora_11, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_11.place(x=0, y=0)
    entry_monitora_11 = tk.Entry(frame_monitora_11, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_11.place(x=87, y=1)
    frame_monitora_11_2 = tk.Label(frame_monitora_11, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_11_2.place(x=5, y=22)
    entry_monitora_11_2 = tk.Entry(frame_monitora_11, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_11_2.place(x=87, y=23)

    frame_monitora_12 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_12.place(x=310, y=340)
    texto_monitora_12 = tk.Label(frame_monitora_12, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_12.place(x=0, y=0)
    entry_monitora_12 = tk.Entry(frame_monitora_12, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_12.place(x=87, y=1)
    frame_monitora_12_2 = tk.Label(frame_monitora_12, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_12_2.place(x=5, y=22)
    entry_monitora_12_2 = tk.Entry(frame_monitora_12, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_12_2.place(x=87, y=23)

    frame_monitora_13 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_13.place(x=15, y=400)
    texto_monitora_13 = tk.Label(frame_monitora_13, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_13.place(x=0, y=0)
    entry_monitora_13 = tk.Entry(frame_monitora_13, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_13.place(x=87, y=1)
    frame_monitora_13_2 = tk.Label(frame_monitora_13, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_13_2.place(x=5, y=22)
    entry_monitora_13_2 = tk.Entry(frame_monitora_13, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_13_2.place(x=87, y=23)

    frame_monitora_14 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_14.place(x=310, y=400)
    texto_monitora_14 = tk.Label(frame_monitora_14, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_14.place(x=0, y=0)
    entry_monitora_14 = tk.Entry(frame_monitora_14, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_14.place(x=87, y=1)
    frame_monitora_14_2 = tk.Label(frame_monitora_14, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_14_2.place(x=5, y=22)
    entry_monitora_14_2 = tk.Entry(frame_monitora_14, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_14_2.place(x=87, y=23)

    frame_monitora_15 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_15.place(x=15, y=460)
    texto_monitora_15 = tk.Label(frame_monitora_15, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_15.place(x=0, y=0)
    entry_monitora_15 = tk.Entry(frame_monitora_15, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_15.place(x=87, y=1)
    frame_monitora_15_2 = tk.Label(frame_monitora_15, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_15_2.place(x=5, y=22)
    entry_monitora_15_2 = tk.Entry(frame_monitora_15, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_15_2.place(x=87, y=23)

    frame_monitora_16 = tk.Frame(frame_cima, width=273, height=50, relief="ridge", borderwidth=2, bg=azul_botao)
    frame_monitora_16.place(x=310, y=460)
    texto_monitora_16 = tk.Label(frame_monitora_16, text="Equipamento: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    texto_monitora_16.place(x=0, y=0)
    entry_monitora_16 = tk.Entry(frame_monitora_16, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_16.place(x=87, y=1)
    frame_monitora_16_2 = tk.Label(frame_monitora_16, text="IP ou Nome: ", font=("Arial", 9, "bold"), bg=azul_botao, fg=branco)
    frame_monitora_16_2.place(x=5, y=22)
    entry_monitora_16_2 = tk.Entry(frame_monitora_16, font=("Arial", 9, "bold"), width= 25)
    entry_monitora_16_2.place(x=87, y=23)

class FrameBaixo:
    #Configuração do frame da parte de baixo
    frame_baixo = tk.Frame(monitor, width=600, height=30, bg=cinza, relief="flat")
    frame_baixo.place(x=0, y=522)

    bt1 = tk.Button(frame_baixo, text='Iniciar', font=("Arial", 10, "bold"), bg=azul_botao, fg=branco, 
                    width=14, command=Iniciar)
    bt1.place(x=0, y=0)

    bt2 = tk.Button(frame_baixo, text='Log', font=("Arial", 10, "bold"), bg=azul_botao, fg=branco, 
                    width=14, command=GerarLog)
    bt2.place(x=121, y=0)

monitor.mainloop()

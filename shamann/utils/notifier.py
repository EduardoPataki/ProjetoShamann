# shamann/utils/notifier.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication # Importar para anexos
import logging
import json
import io # Para lidar com o anexo em memória

# Configuração de logging para este módulo
logger = logging.getLogger(__name__)

class Notifier:
    """
    Gerencia o envio de notificações por e-mail para diferentes níveis de alerta.
    As configurações de SMTP podem ser carregadas de variáveis de ambiente ou passadas diretamente.
    """
    def __init__(self, smtp_server: str = None, smtp_port: int = None, smtp_user: str = None, smtp_password: str = None, sender_email: str = None):
        # Prioriza variáveis de ambiente, mas permite passar direto para testes
        self.smtp_server = smtp_server if smtp_server else os.getenv('SHAMANN_SMTP_SERVER')
        self.smtp_port = smtp_port if smtp_port else int(os.getenv('SHAMANN_SMTP_PORT', 587))
        self.smtp_user = smtp_user if smtp_user else os.getenv('SHAMANN_SMTP_USER')
        self.smtp_password = smtp_password if smtp_password else os.getenv('SHAMANN_SMTP_PASSWORD')
        self.sender_email = sender_email if sender_email else os.getenv('SHAMANN_SENDER_EMAIL', self.smtp_user)

        # Validação básica das configurações
        if not all([self.smtp_server, self.smtp_user, self.smtp_password]):
            logger.error("Configurações SMTP incompletas. Verifique variáveis de ambiente ou parâmetros do Notifier.")
            raise ValueError("Configurações SMTP ausentes para o Notifier.")

        logger.info(f"Notifier inicializado com SMTP Server: {self.smtp_server}:{self.smtp_port}")

    def send_email(self, to_addresses: list[str], subject: str, body: str, is_html: bool = False, attachments: list = None):
        """
        Envia um e-mail para os destinatários especificados, com suporte a anexos.
        :param to_addresses: Uma lista de strings, contendo os endereços de e-mail dos destinatários.
        :param subject: O assunto do e-mail.
        :param body: O corpo do e-mail.
        :param is_html: Booleano, True se o corpo for HTML, False para texto simples.
        :param attachments: Lista de tuplas (file_content, filename, mime_type) para anexos.
        """
        if not to_addresses:
            logger.warning("Nenhum endereço de e-mail de destinatário fornecido. E-mail não enviado.")
            return False

        msg = MIMEMultipart() # Usamos MIMEMultipart para suportar texto/HTML e anexos
        msg['From'] = self.sender_email
        msg['To'] = ", ".join(to_addresses)
        msg['Subject'] = subject

        # Corpo do e-mail (texto ou HTML)
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        # Anexos
        if attachments:
            for content, filename, mime_type in attachments:
                part = MIMEApplication(content, Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                msg.attach(part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender_email, to_addresses, msg.as_string())
            logger.info(f"E-mail '{subject}' enviado com sucesso para {', '.join(to_addresses)}.")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Erro de autenticação SMTP. Verifique usuário/senha: {e}", exc_info=True)
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"Erro ao conectar ao servidor SMTP: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar e-mail: {e}", exc_info=True)
            return False

    def _generate_alert_summary(self, alert_details: dict, lang: str) -> str:
        """Gera um resumo conciso do alerta para o corpo do e-mail."""
        summary_templates = {
            'pt': {
                'subject': "ALERTA CRÍTICO DE SEGURANÇA: {problem_summary} em {host_info}",
                'body_header': "Prezada equipe,\n\nUm **Alerta de Segurança CRÍTICO** foi detectado com urgência:\n",
                'type_label': "Tipo de Alerta",
                'problem_label': "Problema Foco",
                'host_label': "Host Afetado",
                'port_label': "Porta/Serviço",
                'action_needed': "\n**AÇÃO URGENTE NECESSÁRIA!** Detalhes completos no anexo 'detalhes_alerta.txt'.",
                'footer': "\n\nAtenciosamente,\nShamann Security Agent"
            },
            'en': {
                'subject': "CRITICAL SECURITY ALERT: {problem_summary} on {host_info}",
                'body_header': "Dear Team,\n\nA **CRITICAL Security Alert** has been detected with urgency:\n",
                'type_label': "Alert Type",
                'problem_label': "Problem Focus",
                'host_label': "Affected Host",
                'port_label': "Port/Service",
                'action_needed': "\n**URGENT ACTION REQUIRED!** Full details in the 'alert_details.txt' attachment.",
                'footer': "\n\nSincerely,\nShamann Security Agent"
            },
            'de': {
                'subject': "KRITISCHER SICHERHEITSALARM: {problem_summary} auf {host_info}",
                'body_header': "Liebes Team,\n\nEin **KRITISCHER Sicherheitsalarm** wurde dringend erkannt:\n",
                'type_label': "Alarmtyp",
                'problem_label': "Problemfokus",
                'host_label': "Betroffener Host",
                'port_label': "Port/Dienst",
                'action_needed': "\n**DRINGENDE MASSNAHMEN ERFORDERLICH!** Vollständige Details im Anhang 'alarmdetails.txt'.",
                'footer': "\n\nMit freundlichen Grüßen,\nShamann Security Agent"
            }
        }

        template = summary_templates.get(lang, summary_templates['en']) # Padrão para Inglês

        # Extraindo informações chave
        host_info = alert_details.get('host', 'N/A')
        port_info = f"{alert_details.get('port', 'N/A')}/{alert_details.get('protocol', 'N/A')}" if alert_details.get('port') else 'N/A'
        problem_summary = alert_details.get('description', 'Alerta de Segurança Crítico')

        # Constrói o assunto
        subject = template['subject'].format(problem_summary=problem_summary, host_info=host_info)

        # Constrói o corpo do resumo
        body_summary = (
            f"{template['body_header']}\n"
            f"- **{template['type_label']}:** {alert_details.get('type', 'Desconhecido')}\n"
            f"- **{template['Problem_label']}:** {problem_summary}\n"
            f"- **{template['host_label']}:** {host_info}\n"
            f"- **{template['port_label']}:** {port_info}\n"
            f"{template['action_needed']}"
            f"{template['footer']}"
        )
        return subject, body_summary.replace("\n", "<br>").replace("**", "<b>") # Para HTML

    def _generate_attachment_content(self, alert_details: dict, lang: str) -> tuple[str, str]:
        """Gera o conteúdo do anexo em formato de texto estruturado (CSV simples)."""
        filename_template = {
            'pt': "detalhes_alerta.txt",
            'en': "alert_details.txt",
            'de': "alarmdetails.txt"
        }
        filename = filename_template.get(lang, filename_template['en'])

        # Cabeçalhos do CSV/TXT
        headers = ["Campo", "Valor"]
        content_lines = [",".join(headers)] # Linha de cabeçalho

        # Adicionar os detalhes do alerta linha por linha
        content_lines.append(f"Tipo de Alerta,{alert_details.get('type', 'Desconhecido')}")
        content_lines.append(f"Descricao,{alert_details.get('description', 'N/A')}")
        content_lines.append(f"Host,{alert_details.get('host', 'N/A')}")
        content_lines.append(f"IP,{alert_details.get('ip_address', 'N/A')}") # Se disponível
        content_lines.append(f"Hostname,{alert_details.get('hostname', 'N/A')}") # Se disponível
        content_lines.append(f"Porta,{alert_details.get('port', 'N/A')}")
        content_lines.append(f"Protocolo,{alert_details.get('protocol', 'N/A')}")
        content_lines.append(f"Servico,{alert_details.get('service_name', 'N/A')}") # Se disponível
        content_lines.append(f"Versao do Servico,{alert_details.get('service_product', '')} {alert_details.get('service_version', '')}") # Se disponível
        content_lines.append(f"Recomendacao,\"{alert_details.get('recommendation', 'N/A').replace('"', '""')}\"") # Escapar aspas
        content_lines.append(f"Nivel de Severidade,{alert_details.get('level', 'Desconhecido')}")

        # Adicionar detalhes JSON brutos
        json_details = json.dumps(alert_details.get('details', {}), indent=2, ensure_ascii=False)
        content_lines.append(f"Detalhes Completos (JSON),\"\"\"{json_details.replace('"', '""')}\"\"\"") # Usar aspas triplas para JSON grande

        full_content = "\n".join(content_lines)
        return full_content, filename

    def send_critical_alert_email(self, alert_details: dict, recipients_internal: list[str], recipients_external: list[str], lang: str = 'en'):
        """
        Envia um e-mail de alerta CRÍTICO, com resumo no corpo e detalhes no anexo.
        :param alert_details: Dicionário contendo os detalhes do alerta.
        :param recipients_internal: Lista de endereços de e-mail da equipe interna.
        :param recipients_external: Lista de endereços de e-mail de clientes/partes externas.
        :param lang: Idioma para o corpo do e-mail e nome do anexo ('pt', 'en', 'de').
        """
        all_recipients = list(set(recipients_internal + recipients_external))

        if not all_recipients:
            logger.warning("Nenhum destinatário especificado para o alerta crítico. E-mail não enviado.")
            return False

        # 1. Gerar assunto e corpo do resumo
        subject, body_summary = self._generate_alert_summary(alert_details, lang)

        # 2. Gerar conteúdo do anexo
        attachment_content, attachment_filename = self._generate_attachment_content(alert_details, lang)

        # Preparar o anexo como uma lista de tuplas
        attachments = [(attachment_content.encode('utf-8'), attachment_filename, 'text/plain')]

        # 3. Enviar o e-mail com o corpo resumido e o anexo
        return self.send_email(
            to_addresses=all_recipients,
            subject=subject,
            body=body_summary,
            is_html=True,
            attachments=attachments
        )

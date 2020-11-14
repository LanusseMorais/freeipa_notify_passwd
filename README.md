# Freeipa notificação

Esse é um script simples que tem o objetivo de notificar por e-mail quando a senha dos usuários do freeipa está perto de expirar visto que o mesmo ainda não tem essa função nativamente.
## Dependências  
- python 2.7
- pip
- cron
- obs: O servidor precisa ser capaz de enviar e-mails.

## Instalação


```bash
cd /tmp
git clone git@github.com:LanusseMorais/freeipa_notify_passwd.git 
cd freeipa_notify_passwd
sudo ./install.sh
```

## Configuração

O script executa uma vez por dia e você precisa alterar as configurações no arquivo /opt/freeipa_notify_passwd/ipa_config.ini de acordo com o seu ambiente.
```
[Login]
user: usuário no freeipa 
password: senha do freeipa
hostname: ipa.exemplo.com

[Option]
notify_days_remaining: 7
email_from:  "notifica@exemplo.com"
email_subject: "Freeipa: sua senha vai expirar."
email_body: "sua senha de acesso ao freeipa vai expirar em poucos dias, acesse o htpps://ipa.exemplo.com  para alterar sua senha."

```

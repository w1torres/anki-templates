# Criar cinco guias com nomes de thread
for ($i = 1; $i -le 10; $i++) {
    Start-Process wt.exe -ArgumentList "new-tab -p 'Threads' -d D:\GIT\templates_anki\anki-templates\scripts"
}

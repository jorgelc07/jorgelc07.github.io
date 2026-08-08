#!/usr/bin/env bash
#
# Publica el sitio en GitHub Pages.
#
#   bash scripts/publicar.sh
#
# Es gratuito: GitHub Pages sobre un repositorio público no cuesta nada y nunca
# pide medio de pago. Este script NO instala software, NO crea cuentas y NO
# acepta ningún plan: solo prepara el repositorio local y sube los cambios.
#
set -euo pipefail

USUARIO="jorgelc07"
REPO="jorgelc07.github.io"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

azul()  { printf '\033[1;34m%s\033[0m\n' "$*"; }
ok()    { printf '  \033[32m✓\033[0m %s\n' "$*"; }
aviso() { printf '  \033[33m!\033[0m %s\n' "$*"; }

azul "1. Regenerando el sitio"
node scripts/build.js
ok "docs/ actualizado"

azul "2. Revisando que no se publique nada indebido"
# Cinturón de seguridad: nada de rutas locales ni credenciales en lo publicado.
if grep -rIl -e 'file://' -e '/Users/' docs/ 2>/dev/null | grep -q .; then
  echo "  ✗ Hay rutas locales en docs/. Abortado."
  grep -rIl -e 'file://' -e '/Users/' docs/
  exit 1
fi
ok "sin rutas locales"

if grep -rIEl '(ghp_|github_pat_|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)' docs/ content/ scripts/ 2>/dev/null | grep -q .; then
  echo "  ✗ Posibles credenciales en el proyecto. Abortado."
  exit 1
fi
ok "sin credenciales"

if pdftotext docs/assets/documentos/cv-jorge-luis-congacha.pdf - 2>/dev/null | grep -qE '3145692372'; then
  echo "  ✗ El CV publicado todavía tiene el teléfono. Ejecuta scripts/preparar_cv.py"
  exit 1
fi
ok "el CV publicado no lleva teléfono"

azul "3. Preparando el repositorio git"
if [ ! -d .git ]; then
  git init -q
  git branch -M main
  git config user.name  "Jorge Luis Congacha"
  git config user.email "j.congacha@uniandes.edu.co"
  ok "repositorio creado"
else
  ok "repositorio ya existente"
fi

git add -A
if git diff --cached --quiet; then
  ok "no hay cambios que registrar"
else
  git commit -q -m "${1:-Actualiza el sitio}"
  ok "cambios registrados"
fi

azul "4. Enviando a GitHub"
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/$USUARIO/$REPO.git"
  ok "remoto configurado → $USUARIO/$REPO"
fi

if git push -u origin main 2>/dev/null; then
  ok "subido"
  echo
  azul "Listo. El sitio estará en https://$USUARIO.github.io en 1–2 minutos."
  echo "  Estado del despliegue: https://github.com/$USUARIO/$REPO/actions"
else
  echo
  aviso "El push no se completó. Casi siempre es por una de estas dos razones:"
  echo
  echo "   a) El repositorio todavía no existe en GitHub."
  echo "      Créalo en https://github.com/new con estos datos exactos:"
  echo "        · Repository name : $REPO"
  echo "        · Visibilidad     : Public   (obligatorio para el plan gratuito)"
  echo "        · NO marques 'Add a README', ni .gitignore, ni licencia."
  echo
  echo "   b) Falta autenticación. Al hacer push, git pide usuario y contraseña:"
  echo "        · Usuario    : $USUARIO"
  echo "        · Contraseña : un token, NO tu clave de GitHub."
  echo "      Se crea gratis en https://github.com/settings/tokens"
  echo "      → 'Generate new token (classic)' → marca solo el permiso 'repo'."
  echo
  echo "   Cuando lo tengas resuelto, vuelve a ejecutar:  bash scripts/publicar.sh"
  echo
  aviso "Después del primer push, activa Pages una sola vez:"
  echo "     https://github.com/$USUARIO/$REPO/settings/pages"
  echo "       · Source : Deploy from a branch"
  echo "       · Branch : main    · Carpeta: /docs    → Save"
  exit 1
fi

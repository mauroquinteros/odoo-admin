# CURRENCY EXCHANGE ERP &middot; [![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

Desarrollo de Addons para adaptación del Nuevo ERP basado en Odoo.

## 🚩 Table of Contents

- [Instalación](#-instalación)
- [Uso de Librerías](#-uso-de-librerías)
- [Lista de Addons](#-lista-de-addons-desarrollados)
- [Exploradores Soportados](#-exploradores-soportados)
- [Licencia](#-licencia)

## 🔧 Instalación

Accionar comandos en la instalación.

```bash
pip install -r requirements.txt
python odoo-bin -i sale_money_exchange,technical_customizer
```

## 📦 Uso de Librerías

```python
import paramiko
import phonenumbers
import randomuser
```

## 💬 Lista de Addons Desarrollados

| Tecnical Name        | Name Module             | 🔰 Application | ◾ Extension |
| -------------------- | ----------------------- | :------------: | :----------: |
| auto_backup          | Auto Respaldo           |       ✔️       |      ❌      |
| l10n_pe_sunat        | Localización Sunat      |       ❌       |      ✔️      |
| base_config          | Configuración Base      |       ❌       |      ✔️      |
| legal_plaft          | Cumplimento Legal       |       ✔️       |      ❌      |
| base_company         | Núcleo JetCompany       |       ✔️       |      ❌      |
| product_services     | PriceList (Servicios)   |       ❌       |      ✔️      |
| account_treasury     | Tesorería               |       ✔️       |      ❌      |
| l10n_pe_currency     | Tipo de cambio Peru     |       ❌       |      ✔️      |
| mail_layout_extra    | Plantillas Extras       |       ❌       |      ✔️      |
| sale_config          | Configuración Ventas    |       ❌       |      ✔️      |
| sale_money_exchange  | Ventas-Cambios Online   |       ✔️       |      ❌      |
| data_migration       | Migración de Data       |       ❌       |      ✔️      |
| technical_customizer | Personalización Técnica |       ✔️       |      ❌      |

## 📜 Licencia

[MIT](https://choosealicense.com/licenses/mit/) Massachusetts Institute of Technology

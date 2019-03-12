# Affichage Dynamique (Digital Signage)
Application d'affichage dynamique utilisée sur le campus de l'INSA Lyon (LyonTech-la Doua)

## Env variables

```
ENV DATABASE_URL postgres://ad@db/ad
ENV SECRET_KEY ''
ENV DJANGO_ENV 'dev'
ENV MAILGUN_KEY ''
ENV MAILGUN_DOMAIN ''
ENV DEFAULT_FROM_EMAIL ''
ENV DEFAULT_GROUP_PK 0 #Pk du groupe ajouté automatiquement à chaque nouveau inscrit
ENV ALLOWED_HOSTS "affichage.bde-insa-lyon.fr"
ENV RECAPTCHA_PUBLIC_KEY ''
ENV RECAPTCHA_PRIVATE_KEY ''
```
## Licence

[![GNU GPL v3.0](http://www.gnu.org/graphics/gplv3-127x51.png)](http://www.gnu.org/licenses/gpl.html)

```
AffichageDynamique - Open Source Digital Signage used in INSA Lyon School of Engineering (France).
Copyright (C) 2019 Romain TORRENTE

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```

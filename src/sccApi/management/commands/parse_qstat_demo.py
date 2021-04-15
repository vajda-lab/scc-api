import pytz

from dateutil import tz
from django.conf import settings
from django.core.management.base import BaseCommand
from dateutil.parser import parse
from django.utils.dateparse import parse_datetime
from rich.console import Console
from rich.table import Table

from sccApi.models import Job
from user_app.models import User


OUTPUT = """
job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID
-----------------------------------------------------------------------------------------------------------------
5980818 0.10000 nf-analysi xrzhou       r     04/14/2021 18:44:37 linga@scc-kb8.scc.bu.edu           1
5980891 0.10000 nf-analysi xrzhou       r     04/14/2021 18:48:41 linga@scc-kb8.scc.bu.edu           1
5980922 0.10000 nf-analysi xrzhou       r     04/14/2021 18:50:43 linga@scc-kb8.scc.bu.edu           1
5980968 0.10000 nf-analysi xrzhou       r     04/14/2021 18:55:13 linga@scc-kb8.scc.bu.edu           1
5981045 0.10000 nf-analysi xrzhou       r     04/14/2021 19:07:47 linga@scc-kb3.scc.bu.edu           1
5981052 0.10000 nf-analysi xrzhou       r     04/14/2021 19:12:38 linga@scc-ka3.scc.bu.edu           1
5981054 0.10000 nf-analysi xrzhou       r     04/14/2021 19:13:39 linga@scc-kb8.scc.bu.edu           1
5981073 0.10000 nf-analysi xrzhou       r     04/14/2021 19:15:42 linga@scc-kb4.scc.bu.edu           1
5981074 0.10000 nf-analysi xrzhou       r     04/14/2021 19:16:40 linga@scc-kb5.scc.bu.edu           1
5981079 0.10000 nf-analysi xrzhou       r     04/14/2021 19:19:17 linga@scc-ka4.scc.bu.edu           1
5981210 0.10000 nf-analysi xrzhou       r     04/14/2021 19:36:32 linga@scc-kb8.scc.bu.edu           1
5981223 0.10000 nf-analysi xrzhou       r     04/14/2021 19:37:31 linga@scc-ka4.scc.bu.edu           1
5981240 0.10000 nf-analysi xrzhou       r     04/14/2021 19:38:29 linga@scc-ka4.scc.bu.edu           1
5981281 0.10000 nf-analysi xrzhou       r     04/14/2021 19:44:34 linga@scc-kb5.scc.bu.edu           1
5981358 0.10000 nf-analysi xrzhou       r     04/14/2021 20:01:42 linga@scc-ka2.scc.bu.edu           1
5981374 0.10000 nf-analysi xrzhou       r     04/14/2021 20:03:28 linga@scc-kb2.scc.bu.edu           1
5981406 0.10000 nf-analysi xrzhou       r     04/14/2021 20:06:28 linga@scc-ka3.scc.bu.edu           1
5981407 0.10000 nf-analysi xrzhou       r     04/14/2021 20:06:28 linga@scc-kb8.scc.bu.edu           1
5981423 0.10000 nf-analysi xrzhou       r     04/14/2021 20:07:29 linga@scc-ka3.scc.bu.edu           1
5981432 0.10000 nf-analysi xrzhou       r     04/14/2021 20:08:29 linga@scc-kb5.scc.bu.edu           1
5981470 0.10000 nf-analysi xrzhou       r     04/14/2021 20:13:32 linga@scc-kb5.scc.bu.edu           1
5981477 0.10000 nf-analysi xrzhou       r     04/14/2021 20:15:31 linga@scc-kb8.scc.bu.edu           1
5981486 0.10000 nf-analysi xrzhou       r     04/14/2021 20:18:30 linga@scc-kb2.scc.bu.edu           1
5981510 0.10000 nf-analysi xrzhou       r     04/14/2021 20:23:30 linga@scc-kb3.scc.bu.edu           1
5981513 0.10000 nf-analysi xrzhou       r     04/14/2021 20:24:30 linga@scc-ka3.scc.bu.edu           1
5981760 0.10000 nf-analysi xrzhou       r     04/14/2021 20:37:58 linga@scc-kb2.scc.bu.edu           1
5981763 0.10000 nf-analysi xrzhou       r     04/14/2021 20:37:58 linga@scc-kb5.scc.bu.edu           1
5981764 0.10000 nf-analysi xrzhou       r     04/14/2021 20:37:58 linga@scc-kb3.scc.bu.edu           1
5981765 0.10000 nf-analysi xrzhou       r     04/14/2021 20:38:58 linga@scc-kb3.scc.bu.edu           1
5981780 0.10000 nf-analysi xrzhou       r     04/14/2021 20:46:02 neuromorphics-pub@scc-eb3.scc.     1
5981781 0.10000 nf-analysi xrzhou       r     04/14/2021 20:47:00 linga@scc-ka3.scc.bu.edu           1
5981783 0.10000 nf-analysi xrzhou       r     04/14/2021 20:48:01 mnemosyne-pub@scc-c03.scc.bu.e     1
5981784 0.10000 nf-analysi xrzhou       r     04/14/2021 20:48:01 neuromorphics-pub@scc-eb4.scc.     1
5981787 0.10000 nf-analysi xrzhou       r     04/14/2021 20:49:00 mnemosyne-pub@scc-c03.scc.bu.e     1
5981788 0.10000 nf-analysi xrzhou       r     04/14/2021 20:50:01 neuromorphics-pub@scc-fc1.scc.     1
5981789 0.10000 nf-analysi xrzhou       r     04/14/2021 20:50:01 neuromorphics-pub@scc-fb1.scc.     1
5981830 0.10000 nf-analysi xrzhou       r     04/14/2021 20:52:02 neuromorphics-pub@scc-ec3.scc.     1
5981841 0.10000 nf-analysi xrzhou       r     04/14/2021 20:52:02 neuromorphics-pub@scc-ea1.scc.     1
5981843 0.10000 nf-analysi xrzhou       r     04/14/2021 20:52:02 neuromorphics-pub@scc-fc2.scc.     1
5981877 0.10000 nf-analysi xrzhou       r     04/14/2021 20:53:01 biophys-pub@scc-gb01.scc.bu.ed     1
5981903 0.10000 nf-analysi xrzhou       r     04/14/2021 20:56:04 linga@scc-kb3.scc.bu.edu           1
5981927 0.10000 nf-analysi xrzhou       r     04/14/2021 21:00:00 biophys-pub@scc-gb01.scc.bu.ed     1
5981972 0.10000 nf-analysi xrzhou       r     04/14/2021 21:01:58 neuromorphics-pub@scc-fc2.scc.     1
5981973 0.10000 nf-analysi xrzhou       r     04/14/2021 21:01:58 neuromorphics-pub@scc-ea1.scc.     1
5981987 0.10000 nf-analysi xrzhou       r     04/14/2021 21:03:34 biophys-pub@scc-gb01.scc.bu.ed     1
5981989 0.10000 nf-analysi xrzhou       r     04/14/2021 21:03:34 neuromorphics-pub@scc-ec3.scc.     1
5981995 0.10000 nf-analysi xrzhou       r     04/14/2021 21:04:07 siggers-pub@scc-bd2.scc.bu.edu     1
5982011 0.10000 nf-analysi xrzhou       r     04/14/2021 21:04:07 neuromorphics-pub@scc-fc2.scc.     1
5982031 0.10000 nf-analysi xrzhou       r     04/14/2021 21:05:07 park-pub@scc-be2.scc.bu.edu        1
5982035 0.10000 nf-analysi xrzhou       r     04/14/2021 21:06:09 park-pub@scc-be2.scc.bu.edu        1
5982036 0.10000 nf-analysi xrzhou       r     04/14/2021 21:06:09 neuromorphics-pub@scc-ec3.scc.     1
5982073 0.10000 nf-analysi xrzhou       r     04/14/2021 21:08:04 mcdaniel-pub@scc-db4.scc.bu.ed     1
5982074 0.10000 nf-analysi xrzhou       r     04/14/2021 21:08:04 park-pub@scc-be2.scc.bu.edu        1
5982081 0.10000 nf-analysi xrzhou       r     04/14/2021 21:11:06 linga@scc-ka2.scc.bu.edu           1
5982087 0.10000 nf-analysi xrzhou       r     04/14/2021 21:11:06 linga@scc-ka1.scc.bu.edu           1
5982093 0.10000 nf-analysi xrzhou       r     04/14/2021 21:12:06 linga@scc-kb3.scc.bu.edu           1
5982094 0.10000 nf-analysi xrzhou       r     04/14/2021 21:12:06 linga@scc-kb2.scc.bu.edu           1
5982095 0.10000 nf-analysi xrzhou       r     04/14/2021 21:12:06 linga@scc-ka1.scc.bu.edu           1
5982098 0.10000 nf-analysi xrzhou       r     04/14/2021 21:13:05 linga@scc-kb8.scc.bu.edu           1
5982099 0.10000 nf-analysi xrzhou       r     04/14/2021 21:13:05 mcdaniel-pub@scc-db4.scc.bu.ed     1
5982100 0.10000 nf-analysi xrzhou       r     04/14/2021 21:13:05 mcdaniel-pub@scc-db4.scc.bu.ed     1
5982105 0.10000 nf-analysi xrzhou       r     04/14/2021 21:13:05 mcdaniel-pub@scc-db4.scc.bu.ed     1
5982106 0.10000 nf-analysi xrzhou       r     04/14/2021 21:13:05 siggers-pub@scc-bd2.scc.bu.edu     1
5982107 0.10000 nf-analysi xrzhou       r     04/14/2021 21:13:05 jjgroup-pub@scc-df4.scc.bu.edu     1
5982111 0.10000 nf-analysi xrzhou       r     04/14/2021 21:14:05 mcdaniel-pub@scc-db4.scc.bu.ed     1
5982115 0.10000 nf-analysi xrzhou       r     04/14/2021 21:15:03 linga@scc-kb8.scc.bu.edu           1
5982118 0.10000 nf-analysi xrzhou       r     04/14/2021 21:16:05 crem-pub@scc-ti4.scc.bu.edu        1
5982124 0.10000 nf-analysi xrzhou       r     04/14/2021 21:17:06 crem-pub@scc-th4.scc.bu.edu        1
5982125 0.10000 nf-analysi xrzhou       r     04/14/2021 21:17:06 spl-pub@scc-um2.scc.bu.edu         1
5982129 0.10000 nf-analysi xrzhou       r     04/14/2021 21:17:06 siggers-pub@scc-bd2.scc.bu.edu     1
5982130 0.10000 nf-analysi xrzhou       r     04/14/2021 21:17:06 spl-pub@scc-um2.scc.bu.edu         1
5982131 0.10000 nf-analysi xrzhou       r     04/14/2021 21:17:06 spl-pub@scc-um2.scc.bu.edu         1
5982132 0.10000 nf-analysi xrzhou       r     04/14/2021 21:17:06 ilya-pub@scc-cb5.scc.bu.edu        1
5982133 0.10000 nf-analysi xrzhou       r     04/14/2021 21:18:12 spl-pub@scc-um2.scc.bu.edu         1
5982134 0.10000 nf-analysi xrzhou       r     04/14/2021 21:18:12 mcdaniel-pub@scc-db4.scc.bu.ed     1
5982135 0.10000 nf-analysi xrzhou       r     04/14/2021 21:18:12 spl-pub@scc-um2.scc.bu.edu         1
5982136 0.10000 nf-analysi xrzhou       r     04/14/2021 21:18:12 spl-pub@scc-um2.scc.bu.edu         1
5982137 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:09 mcdaniel-pub@scc-db4.scc.bu.ed     1
5982138 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:09 spl-pub@scc-um2.scc.bu.edu         1
5982140 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:09 park-pub@scc-be2.scc.bu.edu        1
5982141 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:09 ilya-pub@scc-cb5.scc.bu.edu        1
5982143 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:09 spl-pub@scc-um2.scc.bu.edu         1
5982144 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:09 mcdaniel-pub@scc-db4.scc.bu.ed     1
5982145 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:09 ilya-pub@scc-be4.scc.bu.edu        1
5982146 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:09 hasselmo-pub@scc-be3.scc.bu.ed     1
5982147 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:09 spl-pub@scc-um2.scc.bu.edu         1
5982148 0.10000 nf-analysi xrzhou       r     04/14/2021 21:19:46 ilya-pub@scc-cb5.scc.bu.edu        1
5982152 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 linga@scc-kb5.scc.bu.edu           1
5982153 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 spl-pub@scc-um2.scc.bu.edu         1
5982155 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 siggers-pub@scc-bd2.scc.bu.edu     1
5982156 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 spl-pub@scc-um2.scc.bu.edu         1
5982157 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 hasselmo-pub@scc-be3.scc.bu.ed     1
5982158 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 ilya-pub@scc-be4.scc.bu.edu        1
5982160 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 ilya-pub@scc-cb5.scc.bu.edu        1
5982161 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 spl-pub@scc-um2.scc.bu.edu         1
5982162 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 spl-pub@scc-um1.scc.bu.edu         1
5982163 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 siggers-pub@scc-bd2.scc.bu.edu     1
5982164 0.10000 nf-analysi xrzhou       r     04/14/2021 21:21:51 spl-pub@scc-um2.scc.bu.edu         1
5982165 0.10000 nf-analysi xrzhou       r     04/14/2021 21:22:44 linga@scc-tm3.scc.bu.edu           1
5982166 0.10000 nf-analysi xrzhou       r     04/14/2021 21:22:44 siggers-pub@scc-bd2.scc.bu.edu     1
5982167 0.10000 nf-analysi xrzhou       r     04/14/2021 21:22:44 ilya-pub@scc-cb5.scc.bu.edu        1
5982168 0.10000 nf-analysi xrzhou       r     04/14/2021 21:22:44 spl-pub@scc-um1.scc.bu.edu         1
5982169 0.10000 nf-analysi xrzhou       r     04/14/2021 21:22:44 crem-pub@scc-th1.scc.bu.edu        1
5982170 0.10000 nf-analysi xrzhou       r     04/14/2021 21:23:40 spl-pub@scc-um1.scc.bu.edu         1
5982171 0.10000 nf-analysi xrzhou       r     04/14/2021 21:23:40 spl-pub@scc-um1.scc.bu.edu         1
5982174 0.10000 nf-analysi xrzhou       r     04/14/2021 21:23:40 spl-pub@scc-um1.scc.bu.edu         1
5982175 0.10000 nf-analysi xrzhou       r     04/14/2021 21:23:40 spl-pub@scc-um2.scc.bu.edu         1
5982176 0.10000 nf-analysi xrzhou       r     04/14/2021 21:26:15 neuromorphics-pub@scc-eb2.scc.     1
5982178 0.10000 nf-analysi xrzhou       r     04/14/2021 21:26:15 neuromorphics-pub@scc-fa3.scc.     1
5982180 0.10000 nf-analysi xrzhou       r     04/14/2021 21:26:15 biophys-pub@scc-gb02.scc.bu.ed     1
5982182 0.10000 nf-analysi xrzhou       r     04/14/2021 21:26:15 ilya-pub@scc-cb5.scc.bu.edu        1
5982184 0.10000 nf-analysi xrzhou       r     04/14/2021 21:26:15 spl-pub@scc-um1.scc.bu.edu         1
5982185 0.10000 nf-analysi xrzhou       r     04/14/2021 21:26:15 spl-pub@scc-um1.scc.bu.edu         1
5982186 0.10000 nf-analysi xrzhou       r     04/14/2021 21:26:15 ilya-pub@scc-cb5.scc.bu.edu        1
5982188 0.10000 nf-analysi xrzhou       r     04/14/2021 21:27:11 neuromorphics-pub@scc-fa2.scc.     1
5982189 0.10000 nf-analysi xrzhou       r     04/14/2021 21:27:11 neuromorphics-pub@scc-eb2.scc.     1
5982199 0.10000 nf-analysi xrzhou       r     04/14/2021 21:28:14 neuromorphics-pub@scc-fc4.scc.     1
5982200 0.10000 nf-analysi xrzhou       r     04/14/2021 21:28:14 neuromorphics-pub@scc-fa3.scc.     1
5982202 0.10000 nf-analysi xrzhou       r     04/14/2021 21:28:14 neuromorphics-pub@scc-fa2.scc.     1
5982203 0.10000 nf-analysi xrzhou       r     04/14/2021 21:28:14 spl-pub@scc-um1.scc.bu.edu         1
5982204 0.10000 nf-analysi xrzhou       r     04/14/2021 21:28:14 ilya-pub@scc-cb5.scc.bu.edu        1
5982206 0.10000 nf-analysi xrzhou       r     04/14/2021 21:28:14 spl-pub@scc-um1.scc.bu.edu         1
5982210 0.10000 nf-analysi xrzhou       r     04/14/2021 21:28:14 spl-pub@scc-um1.scc.bu.edu         1
5982216 0.10000 nf-analysi xrzhou       r     04/14/2021 21:29:11 neuromorphics-pub@scc-fc3.scc.     1
5982217 0.10000 nf-analysi xrzhou       r     04/14/2021 21:29:11 rnaseq-pub@scc-tg2.scc.bu.edu      1
5982218 0.10000 nf-analysi xrzhou       r     04/14/2021 21:29:11 spl-pub@scc-um1.scc.bu.edu         1
5982219 0.10000 nf-analysi xrzhou       r     04/14/2021 21:29:11 spl-pub@scc-um1.scc.bu.edu         1
5982220 0.10000 nf-analysi xrzhou       r     04/14/2021 21:30:11 neuromorphics-pub@scc-fc4.scc.     1
5982221 0.10000 nf-analysi xrzhou       r     04/14/2021 21:30:11 spl-pub@scc-um1.scc.bu.edu         1
5982222 0.10000 nf-analysi xrzhou       r     04/14/2021 21:30:11 rnaseq-pub@scc-tg2.scc.bu.edu      1
5982223 0.10000 nf-analysi xrzhou       r     04/14/2021 21:31:08 crem-pub@scc-ti4.scc.bu.edu        1
5982226 0.10000 nf-analysi xrzhou       r     04/14/2021 21:31:08 neuromorphics-pub@scc-fc3.scc.     1
5982227 0.10000 nf-analysi xrzhou       r     04/14/2021 21:31:08 spl-pub@scc-um1.scc.bu.edu         1
5982228 0.10000 nf-analysi xrzhou       r     04/14/2021 21:31:08 rnaseq-pub@scc-tg2.scc.bu.edu      1
5982229 0.10000 nf-analysi xrzhou       r     04/14/2021 21:31:08 spl-pub@scc-um1.scc.bu.edu         1
5982240 0.10000 nf-analysi xrzhou       r     04/14/2021 21:32:08 neuromorphics-pub@scc-fa2.scc.     1
5982242 0.10000 nf-analysi xrzhou       r     04/14/2021 21:33:10 neuromorphics-pub@scc-fc1.scc.     1
5982243 0.10000 nf-analysi xrzhou       r     04/14/2021 21:33:10 neuromorphics-pub@scc-fa3.scc.     1
5982244 0.10000 nf-analysi xrzhou       r     04/14/2021 21:33:10 neuromorphics-pub@scc-fc4.scc.     1
5982245 0.10000 nf-analysi xrzhou       r     04/14/2021 21:33:10 rnaseq-pub@scc-tg2.scc.bu.edu      1
5982246 0.10000 nf-analysi xrzhou       r     04/14/2021 21:33:10 neuromorphics-pub@scc-ea1.scc.     1
5982247 0.10000 nf-analysi xrzhou       r     04/14/2021 21:33:10 spl-pub@scc-um1.scc.bu.edu         1
5982249 0.10000 nf-analysi xrzhou       r     04/14/2021 21:33:39 neuromorphics-pub@scc-fc1.scc.     1
5982254 0.10000 nf-analysi xrzhou       r     04/14/2021 21:34:40 neuromorphics-pub@scc-fb1.scc.     1
5982255 0.10000 nf-analysi xrzhou       r     04/14/2021 21:34:40 neuromorphics-pub@scc-eb3.scc.     1
5982260 0.10000 nf-analysi xrzhou       r     04/14/2021 21:34:40 neuromorphics-pub@scc-fc3.scc.     1
5982261 0.10000 nf-analysi xrzhou       r     04/14/2021 21:34:40 neuromorphics-pub@scc-ec3.scc.     1
5982266 0.10000 nf-analysi xrzhou       r     04/14/2021 21:34:40 biophys-pub@scc-gb01.scc.bu.ed     1
5982273 0.10000 nf-analysi xrzhou       r     04/14/2021 21:35:41 neuromorphics-pub@scc-eb2.scc.     1
5982274 0.10000 nf-analysi xrzhou       r     04/14/2021 21:35:41 rnaseq-pub@scc-tg3.scc.bu.edu      1
5982275 0.10000 nf-analysi xrzhou       r     04/14/2021 21:35:41 rnaseq-pub@scc-tg2.scc.bu.edu      1
5982276 0.10000 nf-analysi xrzhou       r     04/14/2021 21:35:41 neuromorphics-pub@scc-ea1.scc.     1
5982277 0.10000 nf-analysi xrzhou       r     04/14/2021 21:35:42 neuromorphics-pub@scc-ec3.scc.     1
5982278 0.10000 nf-analysi xrzhou       r     04/14/2021 21:36:39 rnaseq-pub@scc-tg2.scc.bu.edu      1
5982279 0.10000 nf-analysi xrzhou       r     04/14/2021 21:36:39 rnaseq-pub@scc-tg2.scc.bu.edu      1
5982280 0.10000 nf-analysi xrzhou       r     04/14/2021 21:36:39 neuromorphics-pub@scc-ea1.scc.     1
5982281 0.10000 nf-analysi xrzhou       r     04/14/2021 21:36:39 biophys-pub@scc-gb01.scc.bu.ed     1
5982284 0.10000 nf-analysi xrzhou       r     04/14/2021 21:37:39 rnaseq-pub@scc-tg3.scc.bu.edu      1
5982285 0.10000 nf-analysi xrzhou       r     04/14/2021 21:37:39 rnaseq-pub@scc-tg2.scc.bu.edu      1
5982286 0.10000 nf-analysi xrzhou       r     04/14/2021 21:38:40 neuromorphics-pub@scc-ea1.scc.     1
5982287 0.10000 nf-analysi xrzhou       r     04/14/2021 21:38:40 spl-pub@scc-um1.scc.bu.edu         1
5982288 0.10000 nf-analysi xrzhou       r     04/14/2021 21:38:40 neuromorphics-pub@scc-ec3.scc.     1
5982289 0.10000 nf-analysi xrzhou       r     04/14/2021 21:38:40 neuromorphics-pub@scc-fc2.scc.     1
5982290 0.10000 nf-analysi xrzhou       r     04/14/2021 21:38:40 spl-pub@scc-um1.scc.bu.edu         1
5982291 0.10000 nf-analysi xrzhou       r     04/14/2021 21:39:40 linga@scc-tm4.scc.bu.edu           1
5982293 0.10000 nf-analysi xrzhou       r     04/14/2021 21:39:40 linga@scc-tm4.scc.bu.edu           1
5982294 0.10000 nf-analysi xrzhou       r     04/14/2021 21:40:41 rnaseq-pub@scc-tg3.scc.bu.edu      1
5982295 0.10000 nf-analysi xrzhou       r     04/14/2021 21:40:41 peloso-pub@scc-tn2.scc.bu.edu      1
5982296 0.10000 nf-analysi xrzhou       r     04/14/2021 21:40:41 neuromorphics-pub@scc-fc2.scc.     1
5982297 0.10000 nf-analysi xrzhou       r     04/14/2021 21:40:41 peloso-pub@scc-tn2.scc.bu.edu      1
5982298 0.10000 nf-analysi xrzhou       r     04/14/2021 21:40:41 spl-pub@scc-um1.scc.bu.edu         1
5982300 0.10000 nf-analysi xrzhou       r     04/14/2021 21:41:39 park-pub@scc-be2.scc.bu.edu        1
5982301 0.10000 nf-analysi xrzhou       r     04/14/2021 21:41:39 park-pub@scc-be2.scc.bu.edu        1
5982302 0.10000 nf-analysi xrzhou       r     04/14/2021 21:41:39 park-pub@scc-be2.scc.bu.edu        1
5982303 0.10000 nf-analysi xrzhou       r     04/14/2021 21:41:39 park-pub@scc-be2.scc.bu.edu        1
5982304 0.10000 nf-analysi xrzhou       r     04/14/2021 21:41:39 peloso-pub@scc-tn2.scc.bu.edu      1
5982305 0.10000 nf-analysi xrzhou       r     04/14/2021 21:42:39 park-pub@scc-be2.scc.bu.edu        1
5982306 0.10000 nf-analysi xrzhou       r     04/14/2021 21:42:39 park-pub@scc-be2.scc.bu.edu        1
5982309 0.10000 nf-analysi xrzhou       r     04/14/2021 21:43:39 hasselmo-pub@scc-be3.scc.bu.ed     1
5982310 0.10000 nf-analysi xrzhou       r     04/14/2021 21:43:39 park-pub@scc-be2.scc.bu.edu        1
5982312 0.10000 nf-analysi xrzhou       r     04/14/2021 21:44:38 hasselmo-pub@scc-be3.scc.bu.ed     1
5982313 0.10000 nf-analysi xrzhou       r     04/14/2021 21:44:38 hasselmo-pub@scc-be3.scc.bu.ed     1
5982314 0.10000 nf-analysi xrzhou       r     04/14/2021 21:44:38 hasselmo-pub@scc-be3.scc.bu.ed     1
5982318 0.10000 nf-analysi xrzhou       r     04/14/2021 21:45:40 hasselmo-pub@scc-be3.scc.bu.ed     1
5982333 0.10000 nf-analysi xrzhou       r     04/14/2021 21:45:40 hasselmo-pub@scc-be3.scc.bu.ed     1
5982350 0.10000 nf-analysi xrzhou       r     04/14/2021 21:46:40 boas-pub@scc-x07.scc.bu.edu        1
5982352 0.10000 nf-analysi xrzhou       r     04/14/2021 21:46:40 boas-pub@scc-x07.scc.bu.edu        1
5982354 0.10000 nf-analysi xrzhou       r     04/14/2021 21:46:40 boas-pub@scc-x07.scc.bu.edu        1
5982356 0.10000 nf-analysi xrzhou       r     04/14/2021 21:46:40 boas-pub@scc-x07.scc.bu.edu        1
5982364 0.10000 nf-analysi xrzhou       r     04/14/2021 21:47:39 rnaseq-pub@scc-tg3.scc.bu.edu      1
5982365 0.10000 nf-analysi xrzhou       r     04/14/2021 21:47:39 rnaseq-pub@scc-tg3.scc.bu.edu      1
5982369 0.10000 nf-analysi xrzhou       r     04/14/2021 21:47:39 rnaseq-pub@scc-tg3.scc.bu.edu      1
5982371 0.10000 nf-analysi xrzhou       r     04/14/2021 21:47:39 crem-pub@scc-ti2.scc.bu.edu        1
5982372 0.10000 nf-analysi xrzhou       r     04/14/2021 21:47:39 peloso-pub@scc-tn2.scc.bu.edu      1
5982373 0.10000 nf-analysi xrzhou       r     04/14/2021 21:47:39 peloso-pub@scc-tn2.scc.bu.edu      1
5982375 0.10000 nf-analysi xrzhou       r     04/14/2021 21:47:39 peloso-pub@scc-tn2.scc.bu.edu      1
5982388 0.10000 nf-analysi xrzhou       r     04/14/2021 21:48:27 laumann-pub@scc-to3.scc.bu.edu     1
5982390 0.10000 nf-analysi xrzhou       r     04/14/2021 21:49:25 mnemosyne-pub@scc-c03.scc.bu.e     1
5982395 0.10000 nf-analysi xrzhou       r     04/14/2021 21:49:25 laumann-pub@scc-to3.scc.bu.edu     1
5982396 0.10000 nf-analysi xrzhou       r     04/14/2021 21:50:27 boas-pub@scc-x07.scc.bu.edu        1
5982397 0.10000 nf-analysi xrzhou       r     04/14/2021 21:50:27 boas-pub@scc-x07.scc.bu.edu        1
5982398 0.10000 nf-analysi xrzhou       r     04/14/2021 21:51:22 boas-pub@scc-x07.scc.bu.edu        1
5982399 0.10000 nf-analysi xrzhou       r     04/14/2021 21:51:22 boas-pub@scc-x07.scc.bu.edu        1
5982405 0.10000 nf-analysi xrzhou       r     04/14/2021 21:52:22 laumann-pub@scc-to3.scc.bu.edu     1
5982412 0.10000 nf-analysi xrzhou       r     04/14/2021 21:52:22 laumann-pub@scc-to3.scc.bu.edu     1
5982413 0.10000 nf-analysi xrzhou       r     04/14/2021 21:53:22 mnemosyne-pub@scc-c03.scc.bu.e     1
5982415 0.10000 nf-analysi xrzhou       r     04/14/2021 21:53:22 laumann-pub@scc-to3.scc.bu.edu     1
5982416 0.10000 nf-analysi xrzhou       r     04/14/2021 21:53:22 biophys-pub@scc-gb03.scc.bu.ed     1
5982417 0.10000 nf-analysi xrzhou       r     04/14/2021 21:53:22 laumann-pub@scc-to3.scc.bu.edu     1
5982422 0.10000 nf-analysi xrzhou       r     04/14/2021 21:54:23 neuro-pub@scc-md3.scc.bu.edu       1
5982427 0.10000 nf-analysi xrzhou       r     04/14/2021 21:54:23 neuro-pub@scc-md3.scc.bu.edu       1
5982430 0.10000 nf-analysi xrzhou       r     04/14/2021 21:54:23 neuro-pub@scc-md3.scc.bu.edu       1
5982433 0.10000 nf-analysi xrzhou       r     04/14/2021 21:54:23 neuro-pub@scc-md3.scc.bu.edu       1
5982441 0.10000 nf-analysi xrzhou       r     04/14/2021 21:54:23 biophys-pub@scc-gb03.scc.bu.ed     1
5982447 0.10000 nf-analysi xrzhou       r     04/14/2021 21:55:24 linga@scc-tm1.scc.bu.edu           1
5982451 0.10000 nf-analysi xrzhou       r     04/14/2021 21:55:24 neuro-pub@scc-md3.scc.bu.edu       1
5982467 0.10000 nf-analysi xrzhou       r     04/14/2021 21:56:26 neuro-pub@scc-md3.scc.bu.edu       1
5982468 0.10000 nf-analysi xrzhou       r     04/14/2021 21:56:26 biophys-pub@scc-gb03.scc.bu.ed     1
5982469 0.10000 nf-analysi xrzhou       r     04/14/2021 21:57:24 neuro-pub@scc-md3.scc.bu.edu       1
5982470 0.10000 nf-analysi xrzhou       r     04/14/2021 21:57:24 biophys-pub@scc-gb03.scc.bu.ed     1
5982471 0.10000 nf-analysi xrzhou       r     04/14/2021 21:57:24 neuro-pub@scc-md3.scc.bu.edu       1
5982475 0.10000 nf-analysi xrzhou       r     04/14/2021 21:57:24 neuromorphics-pub@scc-eb4.scc.     1
5982480 0.10000 nf-analysi xrzhou       r     04/14/2021 21:58:25 sgrace-pub@scc-db2.scc.bu.edu      1
5982481 0.10000 nf-analysi xrzhou       r     04/14/2021 21:58:25 sgrace-pub@scc-db2.scc.bu.edu      1
5982484 0.10000 nf-analysi xrzhou       r     04/14/2021 21:58:25 sgrace-pub@scc-db2.scc.bu.edu      1
5982485 0.10000 nf-analysi xrzhou       r     04/14/2021 21:58:25 sgrace-pub@scc-db2.scc.bu.edu      1
5982486 0.10000 nf-analysi xrzhou       r     04/14/2021 21:58:25 sgrace-pub@scc-db2.scc.bu.edu      1
5982488 0.10000 nf-analysi xrzhou       r     04/14/2021 21:59:26 sgrace-pub@scc-db2.scc.bu.edu      1
5982489 0.10000 nf-analysi xrzhou       r     04/14/2021 21:59:26 sgrace-pub@scc-db2.scc.bu.edu      1
5982490 0.10000 nf-analysi xrzhou       r     04/14/2021 21:59:26 sgrace-pub@scc-db2.scc.bu.edu      1
5982491 0.10000 nf-analysi xrzhou       r     04/14/2021 22:00:28 sgrace-pub@scc-db2.scc.bu.edu      1
5982492 0.10000 nf-analysi xrzhou       r     04/14/2021 22:00:28 sgrace-pub@scc-db2.scc.bu.edu      1
5982493 0.10000 nf-analysi xrzhou       r     04/14/2021 22:00:28 sgrace-pub@scc-db2.scc.bu.edu      1
5982494 0.10000 nf-analysi xrzhou       r     04/14/2021 22:01:25 biophys-pub@scc-gb02.scc.bu.ed     1
5982496 0.10000 nf-analysi xrzhou       r     04/14/2021 22:01:25 biophys-pub@scc-gb02.scc.bu.ed     1
5982497 0.10000 nf-analysi xrzhou       r     04/14/2021 22:01:25 sgrace-pub@scc-db2.scc.bu.edu      1
5982499 0.10000 nf-analysi xrzhou       r     04/14/2021 22:02:27 crem-pub@scc-th4.scc.bu.edu        1
5982500 0.10000 nf-analysi xrzhou       r     04/14/2021 22:02:27 crem-pub@scc-th1.scc.bu.edu        1
5982503 0.10000 nf-analysi xrzhou       r     04/14/2021 22:03:56 crem-pub@scc-th2.scc.bu.edu        1
5982504 0.10000 nf-analysi xrzhou       r     04/14/2021 22:03:56 crem-pub@scc-th4.scc.bu.edu        1
5982506 0.10000 nf-analysi xrzhou       r     04/14/2021 22:03:56 crem-pub@scc-th2.scc.bu.edu        1
5982507 0.10000 nf-analysi xrzhou       r     04/14/2021 22:03:56 crem-pub@scc-th1.scc.bu.edu        1
5982508 0.10000 nf-analysi xrzhou       r     04/14/2021 22:03:56 biophys-pub@scc-gb02.scc.bu.ed     1
5982510 0.10000 nf-analysi xrzhou       r     04/14/2021 22:04:55 crem-pub@scc-tj1.scc.bu.edu        1
5982511 0.10000 nf-analysi xrzhou       r     04/14/2021 22:04:55 crem-pub@scc-ti2.scc.bu.edu        1
5982512 0.10000 nf-analysi xrzhou       r     04/14/2021 22:04:55 crem-pub@scc-tj1.scc.bu.edu        1
5982513 0.10000 nf-analysi xrzhou       r     04/14/2021 22:04:55 ilya-pub@scc-be4.scc.bu.edu        1
5982514 0.10000 nf-analysi xrzhou       r     04/14/2021 22:04:55 crem-pub@scc-ti2.scc.bu.edu        1
5982515 0.10000 nf-analysi xrzhou       r     04/14/2021 22:04:55 crem-pub@scc-th4.scc.bu.edu        1
5982516 0.10000 nf-analysi xrzhou       r     04/14/2021 22:05:54 crem-pub@scc-th2.scc.bu.edu        1
5982517 0.10000 nf-analysi xrzhou       r     04/14/2021 22:05:54 crem-pub@scc-th2.scc.bu.edu        1
5982518 0.10000 nf-analysi xrzhou       r     04/14/2021 22:05:54 crem-pub@scc-tj1.scc.bu.edu        1
5982519 0.10000 nf-analysi xrzhou       r     04/14/2021 22:05:54 crem-pub@scc-th1.scc.bu.edu        1
5982521 0.10000 nf-analysi xrzhou       r     04/14/2021 22:06:52 apolkovnikov-pub@scc-tj4.scc.b     1
5982522 0.10000 nf-analysi xrzhou       r     04/14/2021 22:06:52 apolkovnikov-pub@scc-tj4.scc.b     1
5982524 0.10000 nf-analysi xrzhou       r     04/14/2021 22:08:52 linga@scc-kb8.scc.bu.edu           1
5982541 0.10000 nf-analysi xrzhou       r     04/14/2021 22:10:51 linga@scc-tl2.scc.bu.edu           1
5982542 0.10000 nf-analysi xrzhou       r     04/14/2021 22:10:51 linga@scc-kb2.scc.bu.edu           1
5982543 0.10000 nf-analysi xrzhou       r     04/14/2021 22:10:51 apolkovnikov-pub@scc-tj4.scc.b     1
5982554 0.10000 nf-analysi xrzhou       r     04/14/2021 22:11:52 linga@scc-kb4.scc.bu.edu           1
5982555 0.10000 nf-analysi xrzhou       r     04/14/2021 22:11:52 linga@scc-kb2.scc.bu.edu           1
5982556 0.10000 nf-analysi xrzhou       r     04/14/2021 22:11:52 linga@scc-ka3.scc.bu.edu           1
5982557 0.10000 nf-analysi xrzhou       r     04/14/2021 22:11:52 linga@scc-ka1.scc.bu.edu           1
5982558 0.10000 nf-analysi xrzhou       r     04/14/2021 22:11:52 linga@scc-ka3.scc.bu.edu           1
5982559 0.10000 nf-analysi xrzhou       r     04/14/2021 22:11:52 linga@scc-ka3.scc.bu.edu           1
5982560 0.10000 nf-analysi xrzhou       r     04/14/2021 22:12:53 linga@scc-ka3.scc.bu.edu           1
5982561 0.10000 nf-analysi xrzhou       r     04/14/2021 22:12:53 linga@scc-kb8.scc.bu.edu           1
5982562 0.10000 nf-analysi xrzhou       r     04/14/2021 22:12:53 linga@scc-ka3.scc.bu.edu           1
5982563 0.10000 nf-analysi xrzhou       r     04/14/2021 22:12:53 linga@scc-kb8.scc.bu.edu           1
5982564 0.10000 nf-analysi xrzhou       r     04/14/2021 22:12:53 linga@scc-ka3.scc.bu.edu           1
5982565 0.10000 nf-analysi xrzhou       r     04/14/2021 22:12:53 linga@scc-kb8.scc.bu.edu           1
5982566 0.10000 nf-analysi xrzhou       r     04/14/2021 22:13:53 linga@scc-kb2.scc.bu.edu           1
5982567 0.10000 nf-analysi xrzhou       r     04/14/2021 22:13:53 linga@scc-ka1.scc.bu.edu           1
5982568 0.10000 nf-analysi xrzhou       r     04/14/2021 22:13:53 linga@scc-kb8.scc.bu.edu           1
5982570 0.10000 nf-analysi xrzhou       r     04/14/2021 22:13:53 linga@scc-ka3.scc.bu.edu           1
5982571 0.10000 nf-analysi xrzhou       r     04/14/2021 22:13:53 linga@scc-kb2.scc.bu.edu           1
5982573 0.10000 nf-analysi xrzhou       r     04/14/2021 22:13:53 linga@scc-ka3.scc.bu.edu           1
5982574 0.10000 nf-analysi xrzhou       r     04/14/2021 22:13:53 linga@scc-kb2.scc.bu.edu           1
5982575 0.10000 nf-analysi xrzhou       r     04/14/2021 22:13:53 linga@scc-kb2.scc.bu.edu           1
5982576 0.10000 nf-analysi xrzhou       r     04/14/2021 22:13:53 budge@scc-he2.scc.bu.edu           1
5982578 0.10000 nf-analysi xrzhou       r     04/14/2021 22:14:52 linga@scc-ka3.scc.bu.edu           1
5982579 0.10000 nf-analysi xrzhou       r     04/14/2021 22:14:52 linga@scc-ka1.scc.bu.edu           1
5982580 0.10000 nf-analysi xrzhou       r     04/14/2021 22:14:52 linga@scc-kb2.scc.bu.edu           1
5982581 0.10000 nf-analysi xrzhou       r     04/14/2021 22:14:52 linga@scc-tl2.scc.bu.edu           1
5982582 0.10000 nf-analysi xrzhou       r     04/14/2021 22:14:52 linga@scc-kb2.scc.bu.edu           1
5982585 0.10000 nf-analysi xrzhou       r     04/14/2021 22:14:52 apolkovnikov-pub@scc-zk2.scc.b     1
5982586 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-ka3.scc.bu.edu           1
5982587 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-kb2.scc.bu.edu           1
5982588 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-ka3.scc.bu.edu           1
5982589 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-kb2.scc.bu.edu           1
5982590 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-ka3.scc.bu.edu           1
5982591 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-kb2.scc.bu.edu           1
5982592 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-ka3.scc.bu.edu           1
5982593 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-kb2.scc.bu.edu           1
5982594 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-ka3.scc.bu.edu           1
5982595 0.10000 nf-analysi xrzhou       r     04/14/2021 22:15:54 linga@scc-ka3.scc.bu.edu           1
5982596 0.10000 nf-analysi xrzhou       r     04/14/2021 22:16:52 linga@scc-kb2.scc.bu.edu           1
5982597 0.10000 nf-analysi xrzhou       r     04/14/2021 22:16:52 linga@scc-kb5.scc.bu.edu           1
5982598 0.10000 nf-analysi xrzhou       r     04/14/2021 22:16:52 linga@scc-kb2.scc.bu.edu           1
5982599 0.10000 nf-analysi xrzhou       r     04/14/2021 22:16:52 linga@scc-ka3.scc.bu.edu           1
5982600 0.10000 nf-analysi xrzhou       r     04/14/2021 22:16:52 linga@scc-kb2.scc.bu.edu           1
5982602 0.10000 nf-analysi xrzhou       r     04/14/2021 22:16:52 linga@scc-ka3.scc.bu.edu           1
5982603 0.10000 nf-analysi xrzhou       r     04/14/2021 22:16:52 linga@scc-kb2.scc.bu.edu           1
5982604 0.10000 nf-analysi xrzhou       r     04/14/2021 22:16:52 linga@scc-ka3.scc.bu.edu           1
5982605 0.10000 nf-analysi xrzhou       r     04/14/2021 22:16:52 linga@scc-kb2.scc.bu.edu           1
5982606 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-ka4.scc.bu.edu           1
5982607 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-kb3.scc.bu.edu           1
5982608 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-ka4.scc.bu.edu           1
5982609 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-kb4.scc.bu.edu           1
5982610 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-kb3.scc.bu.edu           1
5982611 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-kb4.scc.bu.edu           1
5982612 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-kb3.scc.bu.edu           1
5982613 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-kb5.scc.bu.edu           1
5982614 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-ka3.scc.bu.edu           1
5982615 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-kb4.scc.bu.edu           1
5982616 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-ka3.scc.bu.edu           1
5982617 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-ka3.scc.bu.edu           1
5982618 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-ka3.scc.bu.edu           1
5982620 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-ka3.scc.bu.edu           1
5982621 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 linga@scc-ka3.scc.bu.edu           1
5982622 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 budge@scc-hd1.scc.bu.edu           1
5982623 0.10000 nf-analysi xrzhou       r     04/14/2021 22:17:52 apolkovnikov-pub@scc-zk2.scc.b     1
5982625 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb3.scc.bu.edu           1
5982628 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-ka1.scc.bu.edu           1
5982629 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb8.scc.bu.edu           1
5982630 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb4.scc.bu.edu           1
5982631 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-ka4.scc.bu.edu           1
5982632 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb2.scc.bu.edu           1
5982633 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb3.scc.bu.edu           1
5982634 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb4.scc.bu.edu           1
5982635 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb2.scc.bu.edu           1
5982636 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb4.scc.bu.edu           1
5982637 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb2.scc.bu.edu           1
5982638 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb4.scc.bu.edu           1
5982639 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb4.scc.bu.edu           1
5982640 0.10000 nf-analysi xrzhou       r     04/14/2021 22:18:52 linga@scc-kb4.scc.bu.edu           1
5982641 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 linga@scc-kb4.scc.bu.edu           1
5982642 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 linga@scc-ka1.scc.bu.edu           1
5982643 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 linga@scc-kb4.scc.bu.edu           1
5982644 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 linga@scc-ka1.scc.bu.edu           1
5982645 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 linga@scc-kb4.scc.bu.edu           1
5982646 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 linga@scc-tk4.scc.bu.edu           1
5982647 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 linga@scc-tk4.scc.bu.edu           1
5982648 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 linga@scc-tk4.scc.bu.edu           1
5982649 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 linga@scc-tk4.scc.bu.edu           1
5982650 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 spl-pub@scc-ul4.scc.bu.edu         1
5982651 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 spl-pub@scc-ul4.scc.bu.edu         1
5982652 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 boas-pub@scc-wp2.scc.bu.edu        1
5982653 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 apolkovnikov-pub@scc-zk2.scc.b     1
5982654 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 apolkovnikov-pub@scc-tj4.scc.b     1
5982655 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 spl-pub@scc-ul4.scc.bu.edu         1
5982656 0.10000 nf-analysi xrzhou       r     04/14/2021 22:19:52 boas-pub@scc-wp2.scc.bu.edu        1
5982657 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-kb3.scc.bu.edu           1
5982658 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-ka4.scc.bu.edu           1
5982660 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-ka4.scc.bu.edu           1
5982661 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-ka4.scc.bu.edu           1
5982662 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-kb4.scc.bu.edu           1
5982663 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-ka1.scc.bu.edu           1
5982664 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-kb4.scc.bu.edu           1
5982665 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-ka1.scc.bu.edu           1
5982666 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-kb4.scc.bu.edu           1
5982667 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-kb4.scc.bu.edu           1
5982668 0.10000 nf-analysi xrzhou       r     04/14/2021 22:20:53 linga@scc-kb4.scc.bu.edu           1
5982669 0.10000 nf-analysi xrzhou       r     04/14/2021 22:21:52 linga@scc-tl4.scc.bu.edu           1
5982670 0.10000 nf-analysi xrzhou       r     04/14/2021 22:21:52 linga@scc-tl4.scc.bu.edu           1
5982671 0.10000 nf-analysi xrzhou       r     04/14/2021 22:21:52 linga@scc-kb1.scc.bu.edu           1
5982672 0.10000 nf-analysi xrzhou       r     04/14/2021 22:21:52 linga@scc-kb1.scc.bu.edu           1
5982673 0.10000 nf-analysi xrzhou       r     04/14/2021 22:21:52 linga@scc-kb1.scc.bu.edu           1
5982675 0.10000 nf-analysi xrzhou       r     04/14/2021 22:21:52 linga@scc-ka3.scc.bu.edu           1
5982676 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-ka4.scc.bu.edu           1
5982677 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-kb4.scc.bu.edu           1
5982678 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-kb1.scc.bu.edu           1
5982679 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-ka1.scc.bu.edu           1
5982680 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-ka4.scc.bu.edu           1
5982681 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-kb4.scc.bu.edu           1
5982682 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-ka1.scc.bu.edu           1
5982683 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-ka4.scc.bu.edu           1
5982684 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-kb4.scc.bu.edu           1
5982685 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-ka1.scc.bu.edu           1
5982686 0.10000 nf-analysi xrzhou       r     04/14/2021 22:22:52 linga@scc-ka4.scc.bu.edu           1
5982687 0.10000 nf-analysi xrzhou       r     04/14/2021 22:23:52 linga@scc-kb4.scc.bu.edu           1
5982689 0.10000 nf-analysi xrzhou       r     04/14/2021 22:23:52 linga@scc-tm2.scc.bu.edu           1
5982690 0.10000 nf-analysi xrzhou       r     04/14/2021 22:23:52 linga@scc-kb4.scc.bu.edu           1
5982691 0.10000 nf-analysi xrzhou       r     04/14/2021 22:23:52 linga@scc-ka1.scc.bu.edu           1
5982692 0.10000 nf-analysi xrzhou       r     04/14/2021 22:23:52 linga@scc-ka4.scc.bu.edu           1
5982693 0.10000 nf-analysi xrzhou       r     04/14/2021 22:23:52 linga@scc-kb4.scc.bu.edu           1
5982694 0.10000 nf-analysi xrzhou       r     04/14/2021 22:24:51 linga@scc-ka3.scc.bu.edu           1
5982695 0.10000 nf-analysi xrzhou       r     04/14/2021 22:24:51 linga@scc-ka3.scc.bu.edu           1
5982696 0.10000 nf-analysi xrzhou       r     04/14/2021 22:24:51 linga@scc-tm3.scc.bu.edu           1
5982697 0.10000 nf-analysi xrzhou       r     04/14/2021 22:24:51 linga@scc-kb3.scc.bu.edu           1
5982699 0.10000 nf-analysi xrzhou       r     04/14/2021 22:24:51 linga@scc-ka4.scc.bu.edu           1
5982700 0.10000 nf-analysi xrzhou       r     04/14/2021 22:24:51 linga@scc-kb5.scc.bu.edu           1
5982701 0.10000 nf-analysi xrzhou       r     04/14/2021 22:24:51 linga@scc-ka4.scc.bu.edu           1
5982702 0.10000 nf-analysi xrzhou       r     04/14/2021 22:25:51 linga@scc-ka4.scc.bu.edu           1
5982703 0.10000 nf-analysi xrzhou       r     04/14/2021 22:25:51 linga@scc-ka1.scc.bu.edu           1
5982704 0.10000 nf-analysi xrzhou       r     04/14/2021 22:25:51 linga@scc-kb3.scc.bu.edu           1
5982705 0.10000 nf-analysi xrzhou       r     04/14/2021 22:25:51 linga@scc-kb5.scc.bu.edu           1
5982706 0.10000 nf-analysi xrzhou       r     04/14/2021 22:25:51 linga@scc-kb4.scc.bu.edu           1
5982707 0.10000 nf-analysi xrzhou       r     04/14/2021 22:25:51 linga@scc-kb1.scc.bu.edu           1
5982708 0.10000 nf-analysi xrzhou       r     04/14/2021 22:25:51 linga@scc-ka4.scc.bu.edu           1
5982709 0.10000 nf-analysi xrzhou       r     04/14/2021 22:25:51 linga@scc-ka1.scc.bu.edu           1
5982710 0.10000 nf-analysi xrzhou       r     04/14/2021 22:25:51 linga@scc-kb3.scc.bu.edu           1
5982711 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-ka4.scc.bu.edu           1
5982712 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-ka1.scc.bu.edu           1
5982713 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-kb8.scc.bu.edu           1
5982714 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-kb4.scc.bu.edu           1
5982715 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-kb5.scc.bu.edu           1
5982716 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-ka4.scc.bu.edu           1
5982717 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-ka1.scc.bu.edu           1
5982718 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-kb3.scc.bu.edu           1
5982719 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-kb5.scc.bu.edu           1
5982720 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-tk4.scc.bu.edu           1
5982722 0.10000 nf-analysi xrzhou       r     04/14/2021 22:26:50 linga@scc-ka4.scc.bu.edu           1
5982723 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-kb4.scc.bu.edu           1
5982724 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-ka4.scc.bu.edu           1
5982725 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-kb5.scc.bu.edu           1
5982726 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-tm2.scc.bu.edu           1
5982727 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-kb3.scc.bu.edu           1
5982728 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-kb4.scc.bu.edu           1
5982729 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-ka4.scc.bu.edu           1
5982730 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-kb5.scc.bu.edu           1
5982732 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-kb3.scc.bu.edu           1
5982733 0.10000 nf-analysi xrzhou       r     04/14/2021 22:27:51 linga@scc-ka4.scc.bu.edu           1
5982735 0.10000 nf-analysi xrzhou       r     04/14/2021 22:28:50 linga@scc-kb8.scc.bu.edu           1
5982736 0.10000 nf-analysi xrzhou       r     04/14/2021 22:28:50 linga@scc-kb5.scc.bu.edu           1
5982737 0.10000 nf-analysi xrzhou       r     04/14/2021 22:28:50 linga@scc-ka1.scc.bu.edu           1
5982738 0.10000 nf-analysi xrzhou       r     04/14/2021 22:28:50 linga@scc-kb2.scc.bu.edu           1
5982739 0.10000 nf-analysi xrzhou       r     04/14/2021 22:28:50 linga@scc-kb1.scc.bu.edu           1
5982740 0.10000 nf-analysi xrzhou       r     04/14/2021 22:28:50 linga@scc-kb8.scc.bu.edu           1
5982741 0.10000 nf-analysi xrzhou       r     04/14/2021 22:29:49 linga@scc-kb5.scc.bu.edu           1
5982742 0.10000 nf-analysi xrzhou       r     04/14/2021 22:29:49 linga@scc-kb8.scc.bu.edu           1
5982743 0.10000 nf-analysi xrzhou       r     04/14/2021 22:29:49 linga@scc-ka4.scc.bu.edu           1
5982744 0.10000 nf-analysi xrzhou       r     04/14/2021 22:29:49 linga@scc-kb3.scc.bu.edu           1
5982745 0.10000 nf-analysi xrzhou       r     04/14/2021 22:29:49 linga@scc-kb5.scc.bu.edu           1
5982746 0.10000 nf-analysi xrzhou       r     04/14/2021 22:29:49 linga@scc-ka1.scc.bu.edu           1
5982747 0.10000 nf-analysi xrzhou       r     04/14/2021 22:29:49 linga@scc-ka4.scc.bu.edu           1
5982748 0.10000 nf-analysi xrzhou       r     04/14/2021 22:29:49 linga@scc-kb3.scc.bu.edu           1
5982749 0.10000 nf-analysi xrzhou       r     04/14/2021 22:30:50 linga@scc-kb5.scc.bu.edu           1
5982750 0.10000 nf-analysi xrzhou       r     04/14/2021 22:30:50 linga@scc-kb3.scc.bu.edu           1
5982751 0.10000 nf-analysi xrzhou       r     04/14/2021 22:30:50 linga@scc-kb8.scc.bu.edu           1
5982752 0.10000 nf-analysi xrzhou       r     04/14/2021 22:30:51 linga@scc-ka4.scc.bu.edu           1
5982753 0.10000 nf-analysi xrzhou       r     04/14/2021 22:30:51 linga@scc-ka1.scc.bu.edu           1
5982755 0.10000 nf-analysi xrzhou       r     04/14/2021 22:31:50 linga@scc-kb8.scc.bu.edu           1
5982756 0.10000 nf-analysi xrzhou       r     04/14/2021 22:31:50 linga@scc-kb2.scc.bu.edu           1
5982757 0.10000 nf-analysi xrzhou       r     04/14/2021 22:31:50 linga@scc-kb3.scc.bu.edu           1
5982758 0.10000 nf-analysi xrzhou       r     04/14/2021 22:31:50 linga@scc-tm4.scc.bu.edu           1
5982759 0.10000 nf-analysi xrzhou       r     04/14/2021 22:31:50 linga@scc-ka1.scc.bu.edu           1
5982761 0.10000 nf-analysi xrzhou       r     04/14/2021 22:32:50 linga@scc-tl2.scc.bu.edu           1
5982762 0.10000 nf-analysi xrzhou       r     04/14/2021 22:32:50 linga@scc-ka1.scc.bu.edu           1
5982763 0.10000 nf-analysi xrzhou       r     04/14/2021 22:32:50 linga@scc-kb2.scc.bu.edu           1
5982764 0.10000 nf-analysi xrzhou       r     04/14/2021 22:32:50 linga@scc-kb8.scc.bu.edu           1
5982765 0.10000 nf-analysi xrzhou       r     04/14/2021 22:32:50 linga@scc-ka4.scc.bu.edu           1
5982766 0.10000 nf-analysi xrzhou       r     04/14/2021 22:32:50 linga@scc-ka1.scc.bu.edu           1
5982767 0.10000 nf-analysi xrzhou       r     04/14/2021 22:32:50 linga@scc-kb2.scc.bu.edu           1
5982768 0.10000 nf-analysi xrzhou       r     04/14/2021 22:33:50 linga@scc-ka1.scc.bu.edu           1
5982769 0.10000 nf-analysi xrzhou       r     04/14/2021 22:33:50 linga@scc-kb3.scc.bu.edu           1
5982770 0.10000 nf-analysi xrzhou       r     04/14/2021 22:33:50 linga@scc-kb5.scc.bu.edu           1
5982771 0.10000 nf-analysi xrzhou       r     04/14/2021 22:33:50 linga@scc-ka1.scc.bu.edu           1
5982772 0.10000 nf-analysi xrzhou       r     04/14/2021 22:33:50 linga@scc-tk4.scc.bu.edu           1
5982773 0.10000 nf-analysi xrzhou       r     04/14/2021 22:33:50 linga@scc-ka1.scc.bu.edu           1
5982774 0.10000 nf-analysi xrzhou       r     04/14/2021 22:34:50 linga@scc-tl3.scc.bu.edu           1
5982775 0.10000 nf-analysi xrzhou       r     04/14/2021 22:34:50 linga@scc-tk4.scc.bu.edu           1
5982777 0.10000 nf-analysi xrzhou       r     04/14/2021 22:34:50 linga@scc-kb8.scc.bu.edu           1
5982778 0.10000 nf-analysi xrzhou       r     04/14/2021 22:34:50 linga@scc-kb2.scc.bu.edu           1
5982779 0.10000 nf-analysi xrzhou       r     04/14/2021 22:35:53 linga@scc-kb3.scc.bu.edu           1
5982780 0.10000 nf-analysi xrzhou       r     04/14/2021 22:35:53 linga@scc-kb2.scc.bu.edu           1
5982782 0.10000 nf-analysi xrzhou       r     04/14/2021 22:35:53 linga@scc-kb8.scc.bu.edu           1
5982783 0.10000 nf-analysi xrzhou       r     04/14/2021 22:35:53 linga@scc-kb2.scc.bu.edu           1
5982784 0.10000 nf-analysi xrzhou       r     04/14/2021 22:35:53 linga@scc-tl3.scc.bu.edu           1
5982786 0.10000 nf-analysi xrzhou       r     04/14/2021 22:35:53 linga@scc-kb8.scc.bu.edu           1
5982787 0.10000 nf-analysi xrzhou       r     04/14/2021 22:35:53 linga@scc-kb8.scc.bu.edu           1
5982788 0.10000 nf-analysi xrzhou       r     04/14/2021 22:36:49 linga@scc-kb5.scc.bu.edu           1
5982789 0.10000 nf-analysi xrzhou       r     04/14/2021 22:37:50 linga@scc-kb2.scc.bu.edu           1
5982790 0.10000 nf-analysi xrzhou       r     04/14/2021 22:37:50 linga@scc-tl2.scc.bu.edu           1
5982791 0.10000 nf-analysi xrzhou       r     04/14/2021 22:38:49 linga@scc-kb8.scc.bu.edu           1
5982792 0.10000 nf-analysi xrzhou       r     04/14/2021 22:38:49 linga@scc-kb8.scc.bu.edu           1
5982793 0.10000 nf-analysi xrzhou       r     04/14/2021 22:38:49 linga@scc-tm1.scc.bu.edu           1
5982794 0.10000 nf-analysi xrzhou       r     04/14/2021 22:38:49 sorenson-pub@scc-mb5.scc.bu.ed     1
5982795 0.10000 nf-analysi xrzhou       r     04/14/2021 22:38:49 rnaseq-pub@scc-mf6.scc.bu.edu      1
5982796 0.10000 nf-analysi xrzhou       r     04/14/2021 22:38:49 qphys-pub@scc-tq4.scc.bu.edu       1
5982797 0.10000 nf-analysi xrzhou       r     04/14/2021 22:39:49 muirheadgroup-pub@scc-tn3.scc.     1
5982798 0.10000 nf-analysi xrzhou       r     04/14/2021 22:39:49 qphys-pub@scc-tq4.scc.bu.edu       1
5982799 0.10000 nf-analysi xrzhou       r     04/14/2021 22:39:49 sorenson-pub@scc-mb8.scc.bu.ed     1
5982800 0.10000 nf-analysi xrzhou       r     04/14/2021 22:39:49 muirheadgroup-pub@scc-tn3.scc.     1
5982801 0.10000 nf-analysi xrzhou       r     04/14/2021 22:39:49 sorenson-pub@scc-mb5.scc.bu.ed     1
5982802 0.10000 nf-analysi xrzhou       r     04/14/2021 22:39:49 rnaseq-pub@scc-mf6.scc.bu.edu      1
5982803 0.10000 nf-analysi xrzhou       r     04/14/2021 22:39:49 qphys-pub@scc-tq4.scc.bu.edu       1
5982804 0.10000 nf-analysi xrzhou       r     04/14/2021 22:39:49 muirheadgroup-pub@scc-tn3.scc.     1
5982805 0.10000 nf-analysi xrzhou       r     04/14/2021 22:39:49 qphys-pub@scc-tq4.scc.bu.edu       1
5982807 0.10000 nf-analysi xrzhou       r     04/14/2021 22:40:51 muirheadgroup-pub@scc-tn3.scc.     1
5982814 0.10000 nf-analysi xrzhou       r     04/14/2021 22:40:51 neuromorphics-pub@scc-mh2.scc.     1
5982815 0.10000 nf-analysi xrzhou       r     04/14/2021 22:40:51 sorenson-pub@scc-mb8.scc.bu.ed     1
5982819 0.00000 nf-analysi xrzhou       qw    04/14/2021 22:41:03                                    1
5982820 0.00000 nf-analysi xrzhou       qw    04/14/2021 22:41:09                                    1
5982822 0.00000 nf-analysi xrzhou       qw    04/14/2021 22:41:14                                    1
5982823 0.00000 nf-analysi xrzhou       qw    04/14/2021 22:41:18                                    1
5982824 0.00000 nf-analysi xrzhou       qw    04/14/2021 22:41:29                                    1
5982825 0.00000 nf-analysi xrzhou       qw    04/14/2021 22:42:09                                    1
5982826 0.00000 nf-analysi xrzhou       qw    04/14/2021 22:42:18                                    1
"""


def parse_output(output):
    lines = [line for line in output.split("\n") if len(line)]
    header_keys = [column for column in lines[0].split(" ") if len(column)]
    print(header_keys)
    # print(header.split(" "))
    rows = []
    for row in lines[2:]:
        data = {}
        columns = [column for column in row.split(" ") if len(column)]
        for column in range(len(columns)):
            data[header_keys[column]] = columns[column]
        rows.append(data)
    return rows


class Command(BaseCommand):
    help = "Delete objects older than 10 days"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(email="jeff.triplett@gmail.com")

        table = Table()

        table.add_column("job-ID")
        table.add_column("prior")
        table.add_column("name")
        table.add_column("user")
        table.add_column("state")
        table.add_column("submit/start")
        table.add_column("at")
        table.add_column("queue")
        table.add_column("slots")
        table.add_column("ja-task-ID")

        rows = parse_output(OUTPUT)
        for row in rows:
            """
            TODO: Do something with `state`
            Possible columns:
            - job-ID
            - prior
            - name
            - user
            - state
            - submit/start
            - at
            - queue
            - slots
            - ja-task-ID
            -"""
            table.add_row(
                row["job-ID"],
                row["prior"],
                row["name"],
                row["user"],
                row["state"],
                row["submit/start"],
                row["at"],
                row["queue"],
                row.get("slots"),
                row.get("ja-task-ID"),
            )

            job_id = row["job-ID"]
            job_state = row["state"]
            job_submitted = f"{row['submit/start']} {row['at']}"  # .replace("/", "-")
            job_submitted = parse(job_submitted)

            if job_submitted:
                job_submitted = pytz.timezone(settings.TIME_ZONE).localize(job_submitted, is_dst=None)

            job, created = Job.objects.update_or_create(
                sge_task_id=job_id,
                user=user,
                defaults={"job_state": job_state, "job_submitted": job_submitted},
            )

        console = Console()
        console.print(table)

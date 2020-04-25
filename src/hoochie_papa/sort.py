# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochiePapa
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


# Note: Except for swapping 0 and 11,
# Changing these may cause self-test errors

CUSTOM_SORT = {
  0:["None (Shuffled)", "order by due"], #Shuffle is applied at the end
  1:["Due (asc)",            "order by due asc"],
  2:["Due (desc)",          "order by due desc"],
  3:["Creation Time (asc)",   "order by id asc"],
  4:["Creation Time (desc)", "order by id desc"],
  5:["Mod Time (asc)",       "order by mod asc"],
  6:["Mod Time (desc)",     "order by mod desc"],
  7:["Left (asc)",          "order by left asc"],
  8:["Left (desc)",        "order by left desc"],
  9:["Factor (asc)",      "order by factor asc"],
 10:["Factor (desc)",    "order by factor desc"],
 11:["Unrestricted Random (High CPU)",  "order by random()"]
}

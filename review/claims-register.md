# Claims register — every load-bearing claim, its current status, its source
Built 2026-09-22 from notes/01-21. THIS FILE WINS over any individual note where they conflict.
Status: SOLID = official/primary source in hand | PRESS = press only | INFER = our inference | OPEN = unconfirmed

## A. Forcing and rainfall
A1  June 2017 peak: 332 mm/24h Bandarban (FFWC Annual Report 2017, Table 2.3) and 343 mm/24h
    (BMD via Islam, Islam & Jeet 2021). Two independent gauge values. ................... SOLID
A2  Rain onset 12 June ~01:00 local (reanalysis) = "early morning of 12 June" (Islam 2021) .. SOLID
A3  Reanalysis underestimates the 2017 event: best_match 220.5 mm vs 343 gauge = 0.64x;
    era5 ~109 mm = ~0.32x. Correction multiplier 1.56 (anchored) ......................... SOLID
A4  ERA5-Land precipitation NOT served by Open-Meteo; "best_match" is an ERA5/ERA5-Land blend
    of undocumented composition. All reanalysis numbers are VIABILITY PROXIES; real study must
    use CDS ERA5-Land hourly + IMERG bracket. Do not cite Open-Meteo numbers in print ...... SOLID
A5  IMERG over Bangladesh +18 to +92% on extremes (opposite sign to ERA5-Land's >=20% under).
    The two bracket the truth -> use as the uncertainty analysis .......................... SOLID (lit)
    [SUPERSEDED by O2: the bracket fails for 2017. The ERA5 85 % claim is Y5]
A6  July 2026: Bandarban 309 mm (7-8 Jul, Daily Star/BMD); Rangamati 287 mm to 8 Jul (BDRCS/BMD);
    Chattogram Ambagan 329 mm to 06:00 9 Jul (BDRCS/BMD) .................................. SOLID
A7  Aug 2023: 44-89 mm/day prolonged; monthly to 10 Aug Bandarban 856, Chattogram 933,
    Rangamati 601 mm (NAWG/UNICEF) ......................................................... SOLID

## B. Observing network  [REVISED — notes/04 superseded by notes/17]
B1  GHCN-Daily: 10 Bangladesh stations; ZERO in the CHT; nearest two (Chattogram airport,
    Cox's Bazar) both at 3.7 m elevation. Verified BG block complete ....................... SOLID
B2  BWDB/FFWC ran **11 rainfall stations in the South Eastern Hill basin** in 2017 (FFWC AR 2017
    Table 2.3) plus river gauges Sangu x2, Matamuhuri x2, Halda x2, Feni, Karnaphuli ...... SOLID
B3  => The "gauge desert" is a desert of INTERNATIONALLY VISIBLE, METEOROLOGICALLY OWNED gauges.
    Hydrological gauges existed, inside the flood institution. Phrase it this way, always .. SOLID
B4  Rangamati has NO FFWC river station (none on Chengi/Maini/Kasalong/upper Karnaphuli);
    FFWC station list confirmed from live table + AR 2017 Table 3.4 ....................... SOLID
B5  Khan et al. (2012) used ONE BMD gauge (Chittagong) and "assumed... representative" ...... SOLID
B6  Gauge density vs a >=16-per-0.2deg benchmark (~1 per 30 km2): BMD-only (~3 in 13,300 km2)
    = ~150x below; BWDB's 11 SE-hill stations, IF all inside the CHT = ~40x below; over the
    whole SE hill basin (20-25k km2, assumed) = ~60-75x below; BMD+BWDB combined upper bound
    ~31x below. Quote as "40-150x depending on which network is counted", and say the BWDB
    station coordinates are not public — that itself is part of the finding ............... SOLID (range)

## C. Inventory
C1  Rabby & Li 730 records; 484 (66.3%) full date, 238 year-only, 8 blank ................. SOLID
C2  13/06/2017: 243 dated failures (Rangamati 146, Bandarban 91, Chittagong 6); median 59 m2 . SOLID
    [SUPERSEDED by Q2: 257 / Rangamati 160]
C3  Date field: "For Google Earth mapping, the date of the image was recorded" (Rabby & Li 2020) SOLID
C4  Rainfall date audit: 15 clusters/446 records; 4 SUSPECT dates = 83 records (18.6%);
    20/07/2017 Khagrachari (73) has ~20 mm on the date, 130 mm four days later, no documented
    event; Khagrachari IS documented in the June sequence (14, 18 June, Ramgarh) .......... SOLID
C5  FALSE POSITIVE: 11/06/2007 (the 127-death Chittagong disaster) flags WEAK at 33 mm.
    => audit produces FLAGS not deletions; reanalysis can miss real events ................ SOLID
C6  '13/06/207' malformed year, 14 records — resolve, don't drop ........................... RESOLVED (Q1)
C7  Cut-slope hypothesis for 20/07/2017: road/camp locations 51% vs 39% — weak, rejected .... SOLID

## D. June 2017 timing  [notes/13 SUPERSEDED by notes/14]
D1  Failure WINDOW, not point: night 12->13 Jun (asleep) -> "just after dawn" -> ~11:00
    (Manikchhari, soldiers). ~11 h progressive sequence .................................... SOLID (press)
    [SUPERSEDED by Q4: 02:30 to ~11:00, nine hours]
D2  Gauge-corrected threshold crossings vs window: empirical 24h (57.4) +31 to +42 h;
    deployed 24h (200) +14 to +25 h; deployed 72h (350) +3 to +14 h; deployed 3h (100) NEVER . SOLID*
    *3h/100 mm "never" holds under uniform scaling only — a smoothed local burst could have
    crossed it. Say so.
D3  ~17 h gap between empirical and deployed 24 h crossings = operational cost of the
    threshold discrepancy. Robust to uniform scaling ...................................... SOLID
    [SUPERSEDED by O5/Q5: 14-18 h]
D4  RETRACTED: "deployed thresholds set too high to use the window" (notes/13). Wrong after
    gauge correction. Do not use ............................................................ RETRACTED
D5  Regime: prolonged ~36 h moderate-intensity accumulation, failures 24-30 h in -> DELAYED
    regime signature (chi ~1-3), not synchronous. Preliminary; RSF inversion NOT done ...... INFER

## E. Thresholds
E1  Deployed (Chittagong City, 2 automated gauges): 100 mm/3h, 200 mm/24h, 350 mm/72h,
    presented as "to initiate landslide occurrence" (IntechOpen 10.5772/intechopen.74743) ... SOLID
    [station count SUPERSEDED by P8: four GSB stations, Chattogram and Cox's Bazar, 2015]
E2  Empirical (Cox's Bazar, Roy et al. 2022): T5 I=3.63D^-0.1313; 57.4 mm/24h; 130 mm/72h .. SOLID
E3  Deployed / empirical = 3.5x (24h), 2.7x (72h). Different districts, different constructions,
    NEITHER reports ROC/FAR. The absence of skill scores is the finding ................... SOLID
E4  RETRACTED: "no empirical I-D threshold exists for the region" — Roy et al. is one.
    Gap is CHT interior + validation + antecedent-state, not existence ..................... RETRACTED

## F. Flash flood, June 2017 (FFWC Annual Report 2017)
F1  Matamuhuri crossed DL at Lama and Chiringa 12 Jun; Sangu crossed + PEAKED at Bandarban
    13 Jun (16.60 m, +135 cm; 2017 peak vs 1988 record 16.80); Halda peaked 13 Jun ........ SOLID
F2  FFWC's own summary: "landslide in June at many places in the South East hilly region" .. SOLID
F3  FFWC flash flood forecast in 2017: "Experimental... April-May... North East region...
    13 stations" => NONE for the SE hills (Sec. 6.1) ...................................... SOLID
F4  DL datum: AR 2017 in mPWD (Sangu Bandarban DL 15.25); current table mMSL (DL 14.80).
    Compare cm-above-DL only .................................................................. SOLID

## G. Institutions, 2017
G1  No operational LEWS anywhere in Bangladesh; CDMP-II Cox's Bazar 2012 community-based;
    NGO efforts "sporadic... failed" (lit.) ................................................. SOLID (lit)
G2  Chittagong Metropolitan web-GIS LEWS published 2018 (after the event) ................... SOLID
G3  => June 2017: observing infrastructure existed for both hazards; warning function for
    neither; Rangamati had neither station nor forecast ................................... SOLID
G4  Operational date of the 2 Chittagong City gauges relative to June 2017 ................. OPEN
    [SUPERSEDED by P8: four stations set up 2015, "not yet functional" in 2018]

## H. August 2023
H1  Sangu at Bandarban 17.63 m = +283 cm DL, 7 Aug (FFWC via press) ....................... PRESS
H2  FFWC bulletin 7 Aug AM: heavy-very heavy rain SE hill basin next 24-48 h ............... PRESS
H3  "Landslide alert issued for Chattogram division" — issuer TBC (BMD by 2026 analogy) ...... PRESS/OPEN
H4  10 killed 8 Aug Bandarban (Kalaghata, Tongkabati, Naikhongchhari, Lama, Thanchi) ....... PRESS
    [SUPERSEDED by R4: 10 deaths from flood and landslides combined]
H5  NAWG #01: Cox's Bazar 5 dead (SHED); 718 homes damaged by landslides; road to Bandarban
    Sadar "snapped due to landslides" .......................................................... SOLID
H6  Bandarban cut off from sub-districts AND from Rangamati (>3 ft water) ................... PRESS
H7  51 deaths total (UNICEF/NAWG) — cause split NOT available ............................. SOLID (no split)

## I. July 2026
I1  Draft Landslide National Early Action Protocol (NEAP): attention/warning/activation
    triggers; BMD issues graded advisories (ICCG SitRep #2, verbatim) ....................... SOLID
I2  BMD Special Warning Bulletin for Landslide No. 05/2026, 7 Jul 13:00; classification at
    UPAZILA and WARD level ("Wards 7, 8, 9 and 14 of CCC") ................................... SOLID
I3  RETRACTED: "district-level, ~8 orders of magnitude" (notes/19). Upazila/ward: ~5-7 orders . RETRACTED
    [5-7 CORRECTED to 4-7 by Y6]
I4  5 Jul forecast -> MoDMR/DDM/BMD/FFWC activated; NDRCC 24/7; district early warning,
    evacuation, shelter (ICCG) ................................................................ SOLID
I5  38,422 in 1,047 shelters (BDRCS SR3); 1,700 shelters activated; ~36,500 displaced ....... SOLID
I6  Rangamati: "comparatively lower risk" 7 Jul -> "upgraded to high... for the first time
    this season" after 287 mm to 8 Jul. Upgrade FOLLOWED the rain ............................. SOLID
I7  Rangamati: 126 landslide incidents (most of any district), 1 death (BDRCS SR3) ........... SOLID
I8  Camps: 8 dead night 6 Jul (3 camps); >=5 students Camp 5 madrasa 8 Jul AFTERNOON;
    UNHCR 15 refugees killed, 4,307 homeless. At HIGH risk, miking, CPP evacuation support .. SOLID
I9  Cox's Bazar host: 5 landslide, 1 wall, 2 drowning of 8 (BDRCS SR3) ..................... SOLID
I10 National toll: GoB 26 (11 Jul) | BDRCS 43 (12 Jul) | media 44 (11 Jul) | UN 59 (22 Jul).
    Always cite source+date ..................................................................... SOLID
I11 Cascade: Bandarban-Ruma/Thanchi blocked; Khagrachari-Rangamati cut at Mahalchhari;
    Baghaichhari/Bilaichhari stranded; Chattogram-Ramgarh under water (BDRCS SR3) ........... SOLID
I12 The Lancet correspondence is health-focused; 0 mentions of warning. Cite for health only .. SOLID

## J. The three-event comparison
J1  Rangamati: 2017 = 146 [now 160, Q2] failures/121 deaths; 2026 = 126 incidents/1 death. Same district,
    comparable forcing (>300 vs 287 mm). Cautions: night-concentrated vs 4-day spread; onset
    timing; incident-count comparability; attribution is inference ........................... SOLID + INFER
J2  Warning layer: none (2017) -> bulletin + alert (2023) -> NEAP + evacuation (2026) ......... SOLID
J3  Residual = EXPOSURE (camps on cut slopes, warned, still buried), not absence/resolution/
    lead time of warning ....................................................................... SOLID + INFER
J4  Night onset in both deep cases (2017; 6 Jul 2026) — but 8 Jul 2026 madrasa was daytime.
    Do NOT claim night onset is THE mechanism; it is one factor ............................. INFER

## K. Competitors / positioning (from the review track — cite, do not fight)
K1  Sarma & Paul 2026 (Mizoram RSF) — same Surma Group; where/how much/WHEN framing ......... SOLID
K2  Sayeem et al. 2026, Adnan et al. 2020 — already make the AUC-inflation argument .......... SOLID
K3  Lucchese & Brenning 2025 — spatial antecedent THRESHOLDS (amount, not timescale) ........ SOLID
K4  "Early-warning systems unfit for compound disasters" (Discover Hazards 2026) — the hook .. SOLID (lit)

## Items still OPEN (in priority order)
1. B6 recompute gauge-density with BWDB's 11 stations included
2. H3 issuer of the 2023 landslide alert  [RESOLVED, R1]
3. G4 when the Chittagong City gauges went live
4. C6 the 14 '13/06/207' records  [RESOLVED, Q1]
5. FFWC flash-flood forecast extension date to SE hills (between 2017 and 2023)
6. Rabby & Li (2018) — the mapping-date methodology (supports C3/C4)

## L. Added while drafting Section 5 (2026-09-22), from BDRCS SitReps 2-3 read verbatim
L1  BDRCS SR3 district table: Cox's Bazar 20 deaths (16 Rohingya), 16 injured (DC office 9-11 Jul);
    camps 15 deaths (UNHCR 10 Jul); Chattogram 5 deaths; Rangamati 1 death, 34 shelters,
    4,265 sheltered vs 3,987 affected; Bandarban deaths not reported ...................... SOLID
L2  Rangamati sheltered > affected (4,265 vs 3,987) -> consistent with precautionary
    evacuation; counts from different sources (NAWG 9 Jul; GoB 9 Jul). Do not read precisely .. INFER
L3  >=21 landslide deaths identifiable 2026: camps 13 (8 on 6 Jul + >=5 Camp 5 madrasa 8 Jul),
    Cox's Bazar host 5, Chattogram 3 (2 children 8 Jul, Rangunia 10 Jul). Matches press 22 ... SOLID
L4  BDRCS SR2 camps at "highest landslide risk": 3, 7, 8E, 8W, 9-14, 16, 18-20, 20Ext.
    Fatal camps 7 and 11 IN the list; 5 and 15 NOT. List date/criteria unstated ............. SOLID (fact) / OPEN (meaning)
L5  Sitakunda UNO confirmed miking in landslide-risk areas before the Jongol Salimpur child death . SOLID
L6  Camp 5 madrasa: 8 Jul AFTERNOON, >=5 students killed, 10 critically injured; after Ukhiya's
    HIGH classification (Bulletin 05, 7 Jul 13:00) ............................................ SOLID
L7  Ukhiya not among units newly upgraded in Bulletin 05 -> implies earlier HIGH; the bulletin in
    force before the 6 Jul deaths not located ................................................. INFER/OPEN

## M. Added while drafting Section 6 (2026-09-22)
M1  H6 correction: the Bandarban approach was under "more than 3 feet" (= 0.9 m), NOT "more than
    a metre". Use 0.9 m ....................................................................... PRESS
M2  2017 Manikchhari: 4 soldiers killed incl. 2 officers, 1 missing (press). District of the
    locality ambiguous in sources (Manikchhari upazila is in Khagrachari; reports say Rangamati).
    Use the locality name only; do not assign a district ...................................... PRESS
M3  2023: NAWG #01 "Road connectivity (communication) and power (electricity) are the most
    impacted areas"; UNICEF "damage of up to 410 kilometres of roads" ........................... SOLID
M4  2026: 241.31 km roads damaged in South Chattogram alone; Chattogram-Cox's Bazar rail line
    suspended near Shomser Para, Kalurghat (BDRCS SR3 citing NAWG 11 Jul); Sapchhari rescue
    after landslide blocked Chattogram-Rangamati highway, 9 Jul (BDRCS SR2) .................... SOLID

## N. Citation corrections from Crossref (2026-09-22) — supersede every earlier note
N1  The Heliyon 2023 LSM review is **Chowdhury, M.S. (2023)**, single author — NOT "Rahman et al."
    as written in notes/01 and outline v1/v2. doi 10.1016/j.heliyon.2023.e17972.
N2  The deployed-threshold chapter (100/200/350 mm) is **Ali, Tunbridge, Bhasin, Akter, Uddin & Khan
    (2018)**, in "Engineering and Mathematical Topics in Rainfall", IntechOpen — NOT Khan & Chang.
N3  ERA5 Bangladesh evaluation = Islam, M.A. & Cartwright, N. (2020), HSJ 65(7):1112-1128.
N4  "The root causes of landslide vulnerability in Bangladesh" = Ahmed, B. (2021), Landslides 18:1707-1720.
N5  Khan et al. antecedent-rainfall paper: Environ Earth Sci 67(1):97-106, print 2012 (online 2011).
N6  Source of the IMERG +18.3 to +92.0% figure is still unconfirmed.

## O. REAL-PRODUCT RERUN (2026-09-22) — SUPERSEDES A3, A5, D2, D3, D4, C4, C5. See notes/22.
O1  ERA5-Land 24 h max 116.3 mm = 0.34 of gauge; IMERG V07 215.5 mm = 0.63. BOTH low ........ SOLID
O2  The opposite-bias bracket premise fails for 2017: IMERG V07 did not overestimate ........ SOLID
O3  Onset 12 Jun 00:00-01:00 in both products = gauge account ............................. SOLID
O4  Gauge-corrected crossings (range over products and 332/343 mm): empirical 24 h 12 Jun
    02:00-08:00 (+16 to +22 h before earliest failures); operational 24 h 12 Jun 19:00-23:00
    (+1 to +5 h); operational 72 h 13 Jun 01:00-05:00 (inside the window); operational 3 h
    crosses under ERA5-Land only (13 Jun 03:00) — not robust .................................. SOLID
O5  Empirical-to-operational 24 h gap = 14-18 h (robust to scaling and product) ............. SOLID
O6  D4 partially reinstated: operational thresholds would have fired 1-5 h before the first
    failures, at night; depends on assumed earliest failure 00:00 ............................. SOLID + INFER
O7  Audit (ERA5-Land): 6 SUSPECT dates / 101 records (22.6%); 2007 disaster SUSPECT (23.9 mm);
    4 dates / 83 records flagged under both proxy and ERA5-Land ............................... SOLID
    [denominator updated by Y1: 101 of 463 = 21.8 %]

## P. Pre-submission check (2026-09-22)
P1  CDMP-II developed a community-based landslide EWS for Cox's Bazar district in 2012 (Ahmed et al.
    2018, IJGI 7:485); a 2010 GoB attempt in Cox's Bazar Municipality "failed due to lack of project
    funding and consequential maintenance" (Ahmed et al. 2020, GNHR 11:446-468) ................. SOLID
P2  "Currently, landslide warnings are given by the Bangladesh Meteorological Department (BMD), and
    are solely based on forecast of heavy rainfall at the regional scale" (Ahmed et al. 2020) .... SOLID
P3  => "No landslide warning in 2017" was TOO STRONG. Correct claim: no DEDICATED landslide warning;
    at most a generic regional heavy-rain caution; no such caution for June 2017 found ......... SOLID
P4  RETRACTED G1 sub-claim: NGO efforts "sporadic... failed" — the quoted wording could not be
    traced to any source in hand. Removed from the text ....................................... RETRACTED
P5  CDMP-II threshold (IJGI 2018): 96 mm in 24 h or 185 mm [duration truncated in extraction] — a
    THIRD threshold set for the region, not yet used in the paper. Consider for §3.4 / §7.3 ..... OPEN
    [RESOLVED by Y2: 185 mm in 48 h]
P6  Camp population: about 1.2 million refugees, most in 33 camps in Cox's Bazar (UN News, Jun 2026) SOLID
P7  Citation fixes: LEWS-lit -> Ahmed et al. 2020 GNHR; CMA-LEWS -> Ahmed et al. 2018 IJGI 7(12):485;
    Roy et al. 2022 pp. 81-94; IMERG-BD removed (uncited; source never confirmed) ............... SOLID
P8  The 100/200/350 mm thresholds belong to the Geological Survey of Bangladesh's four automated
    stations in Chattogram and Cox's Bazar (2015); "the system is not yet functional and publicly
    available, and requires improvements" (Ahmed et al. 2018, IJGI). => call them INSTALLED, not
    operational. Strengthens the institutional argument .................................... SOLID
P9  Bulletin 05/2026 dates of bulletins 01-04 unknown; removed "within two days" ............. RETRACTED
P10 Upazila area "200-500 km2" unverified -> "a few hundred square kilometres" ............... SOFTENED

## Q. Issue-fixing pass (2026-09-23)
Q1  C6 RESOLVED. The 14 records dated "13/06/207" are 13 June 2017, not 2007. All 14 are in
    Rangamati at Manikchhari/Masjid Para/Police Line Sadar; the 2007 cluster is entirely in
    Chittagong district; their centroid lies inside the 13 Jun 2017 cluster; ERA5-Land gives
    116.3 mm/24h there on 13 Jun 2017 against 23.1 mm on 13 Jun 2007. Correction is applied in
    data/scripts/rain_analysis.py (DATE_FIXES) so it is reproducible ......................... SOLID
Q2  Counts revised: 13 Jun 2017 cluster 243 -> **257** (Rangamati 146 -> **160**, Bandarban 91,
    Chittagong 6). Median scar unchanged at 59 m2. Audit now 15 dates covering **460** records.
    Cluster is 3.5x the next largest (was "a factor of three") ................................ SOLID
Q3  Deep-case centroid moves 0.5 km with the 14 added; same ERA5-Land cell, K and all crossing
    times identical. No analysis result changes ............................................... SOLID
Q4  D1 SUPERSEDED. Failure window now rests on published clock times, not on inference from
    "asleep": Bandarban "around 2:30am" and Cox's Bazar "around 3am" on 13 Jun (Dhaka Tribune,
    13 Jun 2017); survivor "just after dawn" (Al Jazeera, 14 Jun 2017); Manikchhari army slide
    "around 11am", four soldiers incl. two officers (Dhaka Tribune; Daily Star) ............... SOLID
Q5  O4/O6 leads recomputed against 02:30: empirical 24 h +18.5 to +24.5 h; installed 24 h
    +3.5 to +7.5 h; installed 72 h -2.5 to +1.5 h (brackets the first failures); installed 3 h
    crosses 03:00 under ERA5-Land only, half an hour AFTER the first failures. Gap between the
    two 24-h thresholds unchanged at 14-18 h ................................................. SOLID
Q6  M2 RESOLVED. Manikchhari is in Rangamati Sadar upazila (Daily Star: "Manikchari, Bedbedi and
    Reserve Bazar areas of Sadar upazila") ................................................... SOLID
Q7  press2017 composite split into DhakaTribune2017, DailyStar2017, AlJazeera2017, each cited for
    the fact it carries. press2023 remains a composite (ReliefWeb blocked) ................. PART DONE

## R. August 2023 moved to primary sources (2026-09-23)
Sources now in corpus/pdf: BDRCS "Flash Flood and Landslide in Chattogram Region" SitRep 1
(7 Aug 2023) and SitRep 2 (16 Aug 2023); ECHO Daily Flash 10 Aug 2023. press2023 retired; no press
composite remains anywhere in the manuscript.
R1  H3 RESOLVED. The landslide alert was issued by the METEOROLOGICAL DEPARTMENT: BMD "issued a
    severe to extremely severe rainfall warning for six districts" and "also issued a landslide
    alert for the Chattogram division because of potential heavy rain" (BDRCS SitRep 1) ....... SOLID
R2  H2 verbatim confirmed: FFWC daily bulletin, morning of 7 Aug, "a chance of heavy to very heavy
    rainfall in the South-eastern hill basin & adjacent upstream parts of Bangladesh in next
    24-48 hours" ............................................................................. SOLID
R3  H1 confirmed and extended: Matamuhuri +199 cm at Lama on 6 Aug afternoon (flood begins);
    Sangu +283 cm on 7 Aug. Chattogram recorded 322 mm in 24 h to 8:00 on 6 Aug (BMD) ......... SOLID
R4  H4 CORRECTED. "Ten people were killed in landslides" was WRONG. BDRCS SitRep 2: "10 deaths
    have been reported resulting from the flood and landslides" — combined, not separated ..... SOLID
R5  NEW, and it changes the arc: 2023 DID act on warning. "More than 200 BDRCS volunteers ...
    disseminated Early Warning Messages (EWM) and helped people in safe evacuation from the
    high-risk prone landslide areas in Bandarban and Chattogram"; ~33,000 in 208 temporary
    shelters, 234 more opened by district administration (SitRep 2); >50,000 in 1,348 flood
    shelters by 10 Aug, >1 million affected (ECHO) ........................................... SOLID
    => Table 1 "Action on warning: Not documented" for 2023 was wrong and is replaced. The step
       from 2023 to 2026 is smaller than the paper implied: evacuation existed in 2023; what 2026
       added is upazila/ward-level bulletins and the tiered protocol.
R6  H6 now primary: "Bandarban city was cut off from most of its sub-districts and Rangamati hill
    district due to impassable roads, including the key entry route from Chattogram, submerged
    under more than 3 feet of water" (SitRep 2); named damaged roads from SitRep 1 ............ SOLID
R7  BDRCS hosts no Aug-2023 flood situation reports on its own server (WordPress media listing
    shows only Cyclone Mocha, dengue and Cyclone Hamoon for 2023); the two SitReps came from the
    user .................................................................................... NOTE

## S. Full read-through of the compiled PDF (2026-09-23)
S1  §7.6 said the 2017 failure window was "eleven-hour" while §3.3 said nine hours after the
    clock-time revision. Corrected to nine ......................................... CONTRADICTION FIXED
S2  §2.4 source list for 2023 named only NAWG and UNICEF; BDRCS SitReps 1-2 and ECHO, which §4.2
    and §6 now rely on, were missing. Added ................................................. FIXED
S3  Figure 2 still showed the pre-BDRCS 2023 lane: "10 killed, Bandarban" (wrong, the 10 are flood
    and landslide together) and no action mark. Now "10 deaths, flood and landslides" plus
    "33,000 sheltered" ...................................................................... FIXED
S4  ECHO citation printed the full 12-word organisation name; bib author shortened to DG ECHO .. FIXED
S5  §4.2 "blocked the Rangamati ... roads" was ambiguous; the source says Bandarban-Rangamati .. FIXED
S6  §4.3 said the advisory/activation split was "the step that neither the 2017 nor the 2023
    arrangements contained", which now contradicts §4.2's evacuation evidence. Changed to
    "formalised, although 2023 acted on its alert without one" ............................... FIXED
S7  §3.5 called CDMP-II "the only documented dedicated effort", ignoring the GSB automated
    stations of §3.4. Now "Two dedicated efforts are documented, and neither was running" ..... FIXED
S8  §7.3 repeated "the two most recent threshold sets" in consecutive sentences ............... FIXED
S9  Figure 2: the 2017 "no dedicated warning" caption overlapped the lane label; shifted ....... FIXED
Read-through also confirmed: no stale counts (257/160/460), no press composites, abstract 150 w,
0 undefined references, all \reg IDs resolve, three TODOs remain (affiliation, email, repo URL).

## W. Rainfall climatology 1950-2025 (2026-09-26)
Source for all: data/results/climatology.json and climatology_annual_maxima.csv, from
data/scripts/climatology.py on ERA5-Land hourly May-Oct 1950-2026 (77 files, each verified at
4,416 h; 2026 = 3,443 h to 21 Sep 10:00 UTC). Uncorrected ERA5-Land; ranks only.
W1  2026 season incomplete (ends 21 Sep); excluded from MK, Sen, GEV and threshold-day trends .. SOLID
W2  Annual max 24h, 1950-2025 (n=76): Rangamati MK Z=-1.20 p=0.23 Sen -2.6 %/dec;
    Bandarban Z=-0.29 p=0.77 Sen -0.6 %/dec. No significant trend ............................ SOLID
W3  Step at 1979: median annual max 24h 1950-78 vs 1979-2025 = 111 vs 92 mm (Rangamati, +21 %),
    123 vs 99 mm (Bandarban, +24 %). Coincides with satellite era (Bell et al. 2021). That the
    step is a reanalysis artefact is INFERENCE, not shown ...................................... INFER
W4  1979-2025 (n=47): 24h Rangamati Z=+1.63 p=0.10 Sen +7.0 %/dec; Bandarban Z=+1.63 p=0.10
    +6.9 %/dec. 72h Rangamati p=0.21 (+6.1 %/dec), Bandarban p=0.095 (+5.5 %/dec) ............. SOLID
W5  Threshold-day counts (thresholds / 2.95): 1979-2025 p = 0.21 (R, 57.4), 0.063 (B, 57.4),
    0.47 (R, 200), 0.66 (B, 200). Full record: R 200-mm days decline p=0.039, gone from 1979.
    Absolute counts (~40 d/season at 57.4) are implausible: the single-event factor over-corrects
    ordinary rain. Use counts for TREND ONLY, never quote a days-per-season figure ............. SOLID
W6  Event-year season maxima (24h, GEV on 1950-2025): 2017 = 116.3 mm R / 120.8 mm B, RP 2.6 y
    at both; 2023 RP 1.6 / 1.2 y; 2026-to-date RP 2.1 / 1.7 y. These are SEASON maxima, an upper
    bound on the event: Rangamati 2023 max fell 27 Aug (event 8-9 Aug); Bandarban 2017 72h max
    fell 25 Jul. ERA5-Land cannot rank the events; do not quote these as event return periods .. SOLID

## Y. Consistency pass (2026-09-26) — full read against register, data and figures
Y1  Three records dated '15/06/217' (Rangunia Eco Park, Chattogram) read as 15/06/2017: 15 km
    from the Rangunia/Gomra records already on that date; '217' admits no other reading in
    2001-2017. Added to DATE_FIXES in rain_analysis.py; audit rerun. 15/06/2017 now 25 records
    (OK, 107.1 mm); audit 15 dates / 463 records; SUSPECT unchanged at 6 dates / 101 records
    (21.8 %); nearest-cell offset now up to 7.1 km. 13 Jun cluster and all crossings unchanged  SOLID
Y2  P5 resolved: CDMP-II threshold is 96 mm in 24 h or 185 mm in 48 h; "no longer active, as no
    follow-up activities or long-term maintenance" (Ahmed et al. 2018, IJGI, verified in PDF) .. SOLID
Y3  Sangu at Bandarban 2026: 15.76 m = +96 cm DL (MSL datum), 8 Jul (Daily Star, 8 Jul 2026) .. PRESS
Y4  2017 deaths: Rangamati 121; national 150-170 by source and date (Dhaka Tribune; Daily Star).
    First published failure time (02:30) is at BANDARBAN; Rangamati's first is "just after dawn",
    so lead times at the Rangamati centroid measured to 02:30 are LOWER BOUNDS ............... PRESS / INFER
Y5  ERA5 underestimates Bangladesh rainfall above the 75th percentile by up to 85 % (Islam &
    Cartwright 2020, N3; notes/11) ........................................................... SOLID (lit)
Y6  Advisory unit vs 59 m2 median scar: upazila (few hundred km2) ~6.5-7 orders; city ward
    (~1-5 km2) ~4-5 orders. Quote "four to seven" ........................................... SOLID (arith)
Y7  Empirical 72 h (130 mm) gauge-corrected crossings: 12 Jun 03:00-11:00, 1-3 h after the
    empirical 24 h crossing (june2017_crossings.json) ....................................... SOLID
Y8  Anchor caveat: the 332/343 mm gauge peak is at Bandarban (~45 km S of the Rangamati centroid);
    no Rangamati gauge value is published. Stated in §2.3 and §7.6 ........................... INFER
Y9  A7 clarified: 856 mm at Bandarban is the MONTHLY total to 10 Aug 2023, not 5-10 Aug.
    With R3 (322 mm/24 h at Chattogram, 6 Aug) 2023 is "sustained", not "moderate" ........... SOLID
Y10 2023 FFWC bulletin (R2) is a RAINFALL outlook; whether a formal flash flood forecast covered
    the SE hills in 2023 remains OPEN (open item 5) ......................................... OPEN
Y11 Data availability now cites the CONCEPT DOI 10.5281/zenodo.22917014; the version DOI
    22917015 is v1.0.0, which lacks the climatology and has the broken figure script ......... NOTE
Y12 Figure 2's July 2026 panel extended to 18 Jul (rain 14-18 Jul at Bandarban 1.5-7.8 mm/day)
    from the climatology season file, identical to the event file to 4e-6 mm over 3-13 Jul ..... SOLID

## Z. Enhancement analyses (2026-09-26/27) — data/scripts/{event2026,bias_qm,skill,shared_clock,camp_slopes}.py
Z1  2026 gauge check: 10 BMD 24-h totals (BDRCS SR2-3, Daily Star) vs same windows (event2026.json):
    ERA5-Land ratio 1.49-4.71, median 2.79, IQR 2.30-3.26; IMERG V07 Late median 2.06 (0.92-3.35).
    Rangamati/Bandarban/Kutubdia at town coordinates; Chattogram (Ambagan) and Cox's Bazar ~1 km.
    3x3 sensitivity: median ratio 2.63 (wettest neighbour) to 3.07 (driest neighbour) ............ SOLID
Z2  Quantile mapping on GHCN Chattogram airport (12 seasons 2008-2024) + Cox's Bazar (5 seasons
    2015-2024), seasons >=170 reported days, 3,036 days: 20->27.5 mm, 100->200.8 mm. 2026
    out-of-sample: flat x2.95 bias +14.2 mm, MAE 52.3; QM median 0.69 of gauge; raw 0.36 (bias_qm.json).
    => bias is intensity-dependent; results bracketed QM (ordinary days) .. flat 2.79 (extremes) .. SOLID
Z3  Skill (skill.json, K_FLAT 2.79): 31 inventory district-dates May-Oct + 6 sitrep = 37 (3 January
    excluded). Empirical 24h POD 0.57 (qm) - 0.73 (flat), alarm days 12-26 (qm) / 32-56 (flat) per
    season; installed 24h POD 0.22-0.38, alarm 1-2 (qm) / 3-8 (flat). Sitrep events: empirical 1.00.
    Sweep: ~5 alarm d -> POD ~0.38 under BOTH corrections; ~10 d -> ~0.5; ~20 d -> ~0.6. 90% CI
    about +/-0.13. POD is a lower bound (image dates); alarm days are not ...................... SOLID
    Sensitivity: recorded date only (no day before) lowers each POD by <=0.03 (detection_recorded_date_only)
Z4  2026 replay, each product corrected by its own 2026 median ratio (event2026.json):
    Rangamati empirical 24h: ERA5 4 Jul 22:00, IMERG 4 Jul 19:00 (>2.5 d before Bulletin 05, 7 Jul 13:00).
    Installed 24h: ERA5 5 Jul 14:00; IMERG 7 Jul 15:00 (2 h AFTER the bulletin); not reached at the
    lowest ratio of either product. Camps empirical: ERA5 4 Jul 17:00, IMERG 5 Jul 11:00; installed
    ERA5 5 Jul 01:00, IMERG 6 Jul 03:00 (~first deaths, early 6 Jul). Camp 5: 8 Jul afternoon .. SOLID
Z5  Camp terrain (camp_slopes.csv/json), Copernicus GLO-30 (2011-15, pre-camp, DSM) in ISCG outlines
    (33 camps): relief 8.0-28.7 m; max slope in any camp 24.3 deg. Fatal vs other Ukhiya (4 vs 22):
    Mann-Whitney p 0.15-0.44 on all metrics. Listed vs unlisted Ukhiya (15 vs 11): relief 18.2 vs
    14.4 m p=0.046; slope p90 p=0.175. Unlisted fatal camps 15, 5 rank 7, 11 of 33 by slope p90;
    listed fatal 7, 11 rank 16, 17. "Cuts set the deaths" is INFERENCE from the null ............ SOLID + INFER
Z6  Shared clock (shared_clock.json), season files, both corrections, Bandarban + Lama:
    2017 empirical 12 Jun 02:00-03:00, installed 24h 12 Jun 06:00-15:00; Matamuhuri DL 12 Jun, Sangu 13 Jun.
    2023 empirical first 31 Jul-2 Aug, then 5-10 of 10 days to 10 Aug; installed 24h 8 Aug (flat) /
    never (qm); installed 72h 8 Aug (flat) / never (qm); rivers 6-7 Aug; slides reported 7 Aug.
    2026 empirical 24-25 Jun (no recorded slide) and 4-5 Jul; installed 24h 25 Jun + 5 Jul (flat),
    5 Jul Lama only (qm); first deaths 6 Jul; rivers 8 Jul ................................ SOLID
Z7  TWO TIMING BUGS FOUND AND FIXED (2026-09-27):
    (a) IMERG hours were labelled at their START while ERA5-Land hours are labelled at their END,
        so every IMERG crossing in the 2017 analysis was 1 h EARLY (rain_analysis.imerg_hourly_point,
        now shifted +1 h). Supersedes the IMERG parts of O4/Q5: empirical 24h 12 Jun 09:00 (lead
        17.5 h, was 18.5); installed 24h 23:00-00:00 (lead 2.5-3.5 h, was 3.5-4.5); installed 72h
        13 Jun 06:00 (was 05:00). Text now "17 to 25 h" and "two to eight h". 14-18 h gap unchanged.
        This bug is in the PUBLISHED v1.1.1 code and results.
    (b) event2026.py and the 2026 check in bias_qm.py added the +6 h BST offset twice (ra.point
        already returns BST). All 2026 numbers in Z1, Z2, Z4 above are from the corrected code;
        the first drafts (median 2.88, crossings 6 h late) are void. skill/shared_clock unaffected
        except via K_FLAT (2.88 -> 2.79) .............................................. FIXED
Z8  Warming sensitivity (warming.json): corrected 1979-2025 series scaled uniformly by 7 %/deg
    (Clausius-Clapeyron; Trenberth 2003, Westra 2014), +1..+3 deg. Alarm days: empirical 24h
    +10-11 %/deg (+30-31 % at 3 deg); installed 24h +17-19 %/deg (+57-62 % at 3 deg, 2.6-7.4 d).
    Installed POD 0.22-0.38 -> 0.30-0.49 at 3 deg. Scaling rain by f == lowering threshold by f,
    so warming moves a fixed trigger ALONG the Fig 2b curve. Sensitivity, not projection ...... SOLID
    (2026-09-27: manuscript restructured to Introduction / Results / Discussion / Methods;
    Acknowledgements-funding and Competing interests added as \todo placeholders for the authors.)
Z9  Rangamati counterfactual: 2017 rate 121/160 = 0.756 deaths per dated failure; x 126 incidents
    (2026) = 95.3 expected vs 1 observed. For consistency each 2026 incident would need ~1/95 the
    lethality of a 2017 failure, or the 2026 count would overstate comparable failures ~95-fold.
    Arithmetic on I7, Q2, Y4; the counts' comparability remains the stated caveat ............. SOLID (arith)
## ZZ. Reviewer-attack checks (2026-09-29) — data/scripts/guards.py -> results/guards.json
Z10 Rangamati forcing, same point, uncorrected: ERA5-Land 2017 max24 116.3 / max72 193.0 / total 213.2
    vs 2026 106.4 / 259.9 / 483.2; IMERG 2017 215.5 / 307.6 / 315.0 vs 2026 (to 10 Jul) 131.3 / 267.1 /
    396.5. 2026 larger totals, lower 24-h peak (-9 % ERA5, -39 % IMERG); 72-h +35 % / -13 %.
    => "comparable forcing" holds for totals, not peak intensity; stated as a fifth qualification .. SOLID
Z11 Reading interval (gauge-anchored 2017): 3-hourly reports first >=57.4 at 12 Jun 03:00 (ERA5) /
    09:00 (IMERG); 6-hourly 06:00 / 12:00 -> 14-24 h before 02:30 13 Jun. Single 06:00 reading:
    146 mm (ERA5) vs 36 mm (IMERG) on 12 Jun; 314/305 mm on 13 Jun (after first failures) ..... SOLID
Z12 Gauge-only alarm days (GHCN daily totals, complete seasons): Chattogram airport >=57.4 14.2 d,
    >=200 1.17 d (12 seasons); Cox's Bazar 19.4 d, 2.40 d (5 seasons). QM daily reproduces these
    (14.7, 1.2; 19.2, 2.4) by construction; flat x2.79 roughly doubles them (31.2, 3.2; 39.4, 5.6).
    Rolling-24h counts exceed daily-total counts (~1.6-1.7x) ....................................... SOLID
Z13 Cox's Bazar only (13 events): empirical POD 0.46 (qm) / 0.69 (flat), alarm 26.0 / 56.4 d;
    installed POD 0.15 / 0.23, alarm 2.4 / 7.5 d. Same trade-off where the empirical threshold
    was derived ..................................................................................... SOLID
Z14 Chance and year robustness (skill.json "robustness", added 2026-10-03). Chance = share of May-Oct
    days in the event's district and year whose day-or-day-before window reaches the threshold.
    Empirical 24h: POD 0.57 (qm) / 0.73 (flat) vs chance 0.16 / 0.36 (factor 3.6 / 2.0); without
    2017 (8 of 37 events) 0.55 / 0.72; leave-one-year-out 0.50-0.60 / 0.69-0.76.
    Installed 24h: POD 0.22 / 0.38 vs chance 0.02 / 0.05; without 2017 0.17 / 0.34; LOYO 0.16-0.24 /
    0.31-0.41. Max LOYO shift 0.07. 18 event years (2002-2017, 2023, 2026). Published Z3 values
    reproduce exactly. Answers the co-author's "won't work for different years" for the skill result
    only; it says nothing about the Rangamati 2017/2026 comparison ................................ SOLID
Z15 Riveros et al. 2026 (NHESS 26:2437) cited in Intro and Discussion: unified RF susceptibility for
    flash flood + landslide, Liguria; static factors only; finds shared controls and overlapping
    area; leaves rainfall/timing/joint occurrence and thresholds to future work (their 5.4, 5.7) .. SOLID

Z16 2017 crossings under other corrections, Rangamati 13-Jun centroid (scratch lead.py, ERA5-Land):
    raw max24 116 mm, empirical 24h 12 Jun 11:00 (+15.5 h), installed never; QM max24 239 mm (0.70
    of 343), empirical 12 Jun 04:00 (+22.5 h), installed 13 Jun 02:00 (+0.5 h); flat 2.95 02:00
    (+24.5 h) / 19:00 (+7.5 h). Empirical lead robust; installed lead depends on the anchor ..... SOLID
Z17 Roy et al. 2022 event dates (their Table 1) vs our Cox's Bazar events: 5 of 13 within 1 day
    (2003-06-15, 2008-07-03, 2010-06-13/14/15). skill.json "independent_of_roy": CXB overlap POD
    0.8 (qm) / 1.0 (flat); CXB independent (n=8) empirical POD 0.25 / 0.50 vs chance 0.22 / 0.43
    (no skill out of sample, n small); installed 0.12 / 0.12 vs 0.02 / 0.07. Pooled without the 5
    (n=32): empirical 0.53 / 0.69 vs chance 0.17 / 0.35; installed 0.22 / 0.38 vs 0.02 / 0.05 .. SOLID
    => Z13 sentence "Nor is the trade-off an artefact..." WITHDRAWN (2026-10-03).
Z18 Inventory Death_ field, 13 Jun 2017: Rangamati 14 deaths at 3 of 160 sites; Bandarban 10 at 3 of
    91; Chattogram 0 of 6. Against 121 reported for Rangamati => mapped scars and fatal slides are
    largely different sets; Z9 deaths-per-failure rate WITHDRAWN from the manuscript ............. SOLID
Z19 Rohingya: >670,000 arrived after 25 Aug 2017 (JRP 2018; other versions 671,000 / 688,000);
    ~212,000 before (ISCG sitreps 2017). From search snippets only; the PDFs were blocked to
    download. VERIFY against the JRP 2018 PDF before submission ...................................... SNIPPET
A1 REVISED 2026-10-03: 343 mm is the BMD station in RANGAMATI town ("The Dhaka Met office said Tuesday
    morning it had recorded 343mm of rainfall in Rangamati over the course of 24 hours", Al Jazeera
    14 Jun 2017; Islam 2021 gives 343 mm without a station). 332 mm = FFWC Bandarban. Y8 ("no
    Rangamati gauge value is published") WITHDRAWN. BMD Rangamati also gave 287 mm (2026, A6).
    Station ~3.4 km from the 160-failure centroid (coords 22.63N 92.15E from a search summary,
    unverified). B1 stands only as "not in GHCN"; "Rangamati had neither" WITHDRAWN ............... PRESS+SOLID

## Open after co-author critique (2026-10-03) — NOT yet addressed in the manuscript
- [ADDRESSED 2026-10-03, Z18] Rangamati 2017 vs 2026 counts are different units; Z9 rate withdrawn.
- [ADDRESSED 2026-10-03, A1 revised] BMD reports Rangamati rainfall (287, 130, 106 mm 2026; 601 mm Aug 2023), so a BMD Rangamati gauge
  exists; "Rangamati had neither", B1-based framing and the gauge recommendation need correcting.
- [ADDRESSED: it is Rangamati, Al Jazeera] Islam 2021 343 mm: quoted text says "southeastern Bangladesh", no station; "at Bandarban" unverified.
- [ADDRESSED, Z19 needs PDF check] Camps barely existed June 2017 (influx from Aug 2017): "deaths moved" is partly exposure change.
- [ADDRESSED, Z16] Installed 24h lead 2-8 h holds under flat scaling only; QM gives 0.5 h (12 Jun 02:00 vs 13 Jun 02:00).
- [ADDRESSED, Z17] Roy 2022 derivation events (30 Cox's Bazar, 1997-2021, BMD) may overlap our 13 Cox's Bazar events.
- Abedin et al. 2020 (Geoenviron Disasters 7:23) on 13 Jun 2017 Rangamati not yet obtained (publisher bot wall).
- [ADDRESSED 2026-10-08] Title now "Landslide deaths in Bangladesh now concentrate in warned refugee camps" (13 of >=21 identifiable 2026 landslide deaths in camps, L3); no 'moved' claim. Fig 4a now plots Rangamati gauge 24-h rain (343 vs 287 mm) and deaths; failure counts dropped (Z18).

## M. Modelling companion study (started 2026-10-04) — modelling/, separate from the npj paper
M1  TRIGRS 2.1.00c (usgs/landslides-trigrs @ 9bb5ec2, code.usgs.gov) built with gfortran on M1
    (trg, tpx); USGS tutorial runs, FS falls from period 1 to 2 with cells < 1 (no reference output
    shipped). Runoff routing skipped (TI files absent; TRIGRS logs "Skipped runoff-routing") ....... SOLID
M2  Domain: 160 Rangamati failures of 13 Jun 2017 +1.5 km, GLO-30 -> UTM46N 30 m, 722 x 477 cells,
    155 failure cells. Slope p10/50/90: all cells 0.0/10.2/24.6 deg; failure cells 6.4/18.1/26.4.
    Forcing = manuscript's gauge-anchored hourly series (343 mm anchor), 10 Jun 01:00-14 Jun 00:00 ... SOLID
M3  Lookup mode (one-row grid of slopes 0-50 deg @0.25) equals full TRIGRS: 60x60 crop, |dFS| <= 0.004
    on slopes >= 5 deg (max 0.18 only on near-flat cells with FS ~10), FS<1 classification agrees on
    100 % of cells. Must delete TRgrid_size.txt before each run (TRIGRS caches grid size) ............ SOLID
M4  30 m slope barely separates failure cells from hillslope: AUC 0.551; share >= 21 deg 0.30 vs 0.26;
    >= 26 deg 0.12 vs 0.12. With uniform parameters FS ranks cells by slope, so 0.551 is the ceiling
    of any such run => TRIGRS at 30 m cannot answer "where"; only "when" ......................... SOLID
M5  Infinite slope, fully saturated: critical slope at the median failure slope (18 deg) is reached
    only at the weak corner of Santo et al. 2024 lab values (c 3.7 kPa, gamma 15.7, z >= 2 m:
    18.2 deg) or with c ~ 0 (phi 27.8 -> 14.4 deg). Central values (c 6, phi 31, gamma 19, z 2): 26 deg . SOLID
M6  Ensemble (ensemble_2017.csv/_summary.json): 400 LHS sets x 2 forcings = 800 runs, 0 errors; 674
    admissible (<5 % hill cells FS<1 before rain). 442 trigger failure cells; median first failure
    23.5 h (p10-p90 3.6-26.5 h) BEFORE 02:30 13 Jun, i.e. 12 Jun early morning, with the empirical
    threshold crossing. 97 runs trigger any cell in the 02:30-11:00 window, 15 a majority; in-window
    share of failure cells median 0.019 (p90 0.086). Delay set by low diffusivity (D0/Ks rho 0.55)
    and deep soil (zmax rho -0.34); in-window runs: Ks 5.7e-7 vs 2.7e-6, D0/Ks 23 vs 67, zmax 3.0 vs
    2.5 m. Failure cells fail no more than hillslope (0.097 vs 0.105); AUC 0.551 in every run (M4).
    Extent driven by cohesion (rho -0.65) ............................................................ SOLID
M7  ICESat-2 ATL08 v007 (59 granules 2018-10..2026-09 found, 31 with ground in domain, 96 tracks,
    24,006 20-m points; icesat2_slopes.json). Heights converted ellipsoid -> EGM2008 (N ~ -52.8 m;
    first pass without it was wrong). DEM - ICESat-2 ground: median 0.4 m (p10 -1.7, p90 7.2).
    60 m baseline, hill points (DEM >= 5 deg): DEM p50/90/95 = 8.0/17.1/19.9 deg; ICESat-2 3.7/19.6/24.5;
    share >= 26 deg 0.8 % vs 3.1 %. Noise floor (DEM < 2 deg) 0.1-0.5 deg. => the 30 m surface model
    both adds slope where ground is gentle and flattens the steepest ground (tail ~2.5-4.6 deg steeper,
    ~4x more >= 26 deg). A statistical correction would raise unstable AREA but cannot place it;
    ASF "12.5 m ALOS" DEM is upsampled SRTM (ASF RTC guide) - not used .............................. SOLID
M8  2026 replay (replay2026_2017.csv/_summary.json): all 674 admissible 2017 sets re-run with July 2026
    forcing anchored the same way (max 24 h at the failure centroid = 287 mm Rangamati BMD, K 2.70
    ERA5 / 2.19 IMERG; flat factor inflates the fortnight to 1,334 / 873 mm). All sets: unstable hill
    share 2017 vs 2026 equal in median (ratio 1.0; 345 equal within 0.5 pp, 208 lower, 121 higher).
    The 97 sets that reproduce the 2017 timing (slow, deep soils): 2026 MORE unstable, 15.4 vs 8.8 %
    of hillslope (ratio 1.93 ERA5, 1.48 IMERG; 67 of 97 higher; corrected from 66 on 2026-10-08), first failures 6 Jul 18:00 (ERA5) /
    7 Jul 15:00 (IMERG), before the assumed 8-11 Jul incident window. => the 2026 storm was at least
    as hazardous as 2017 in this model; with soils that fit 2017's timing it was more so. Caveats:
    30 m (M4), flat correction over two weeks, 2026 incident dates unknown ............................ SOLID
M9  PCMCI+ lag structure (pcmci_lags.py -> pcmci_lags.json; tigramite 5.2.10, RobustParCorr, tau_max
    5 d, pc_alpha 0.01, rain exogenous). ERA5-Land daily (00 UTC fields; UTC day = 06:00-06:00 BST)
    May-Oct 2001-2026 (4,727 days), anomalies from a 31-day smoothed DOY climatology, at the inventory
    centroids (Rangamati 22.661/92.175, Bandarban 22.107/92.246). sm3 = swvl3 (28-100 cm), sro = surface
    runoff, ssro = ro - sro. Both points: rain -> sro same day, strongest link (val 0.68 Rangamati,
    0.83 Bandarban); rain -> sm3 same day (0.19 / 0.31), sm3 memory 1-2 d (lag-1 val 0.70 / 0.76);
    ssro driven by sm3 (Rangamati lag 1, 0.12; Bandarban same day, 0.40) with memory 2-4 d. Rain
    -> sro and rain -> sm3 at lag 0 hold under ParCorr, pc_alpha 0.05 and both halves (2001-13,
    2014-26). Order: quickflow and deep-soil wetting on the storm day, slow (river-sustaining)
    runoff after. Event composite thin: Rangamati n = 2 (2017, 2026) sro and sm3 peak on the UTC
    day before the BST date (= the storm day), ssro peaks +2 d; Bandarban n = 5, ssro shows no rise.
    Hourly, Rangamati June 2017: rain and sro peak 03:00 BST 13 Jun, sm3 peak 04:00, i.e. within
    1.5 h after the first failures (02:30); sm3 had made 96 % of its rise by then, ssro was at 18 %
    of its peak (15 Jun 22:00). July 2026: rain/sro peak 7 Jul 16:00, sm3 9 Jul 03:00, ssro 9 Jul
    23:00. Bandarban sm3 sits at 0.40-0.43 (near the model's saturation) through July 2026, so ssro
    there answers the burst at once (2017: sro and ssro both 12 Jun 08:00). CAVEATS: every variable
    is from one land-surface model, so the graph is that model's internal order, not observation;
    9 km cells; Kaptai Lake regulates the Karnaphuli at Rangamati, so ssro there is not a river
    stage. GloFAS discharge checked later, see M11 ..................... SOLID
M10 Flood model, Sangu above Bandarban (LISFLOOD-FP 8.x inertial solver; prep_sangu.py, run_lisflood.py,
    lisflood_overlay.py -> results/lisflood/<event>_fr1/). GLO-30 at 90 m, catchment 2,158 km2, D4-
    conditioned; IMERG V07 half-hourly on 900 m tiles, catchment only, one scale factor per storm
    anchored to the station record (2017 x1.91, 2026 x2.10); sub-grid channel w = 2.6 A^0.5; n 0.05
    floodplain, 0.035 channel; NO infiltration (the scalar keyword is ignored by the sub-grid solver,
    so the intended 2 mm/h never applied; only an infilfile grid works); max_Froude 1. FIRST RUNS (_base) INVALID: without
    the Froude limiter the sub-grid channel created water (2026: stored 5.9e9 m3 against 2.1e9 m3 of
    rain; 30 m stage; Qout 66,560 m3/s); the internal Verror column did not show it. 36 h tests on
    2026: stored/rain 8.47 unchanged, 1.29 cfl 0.3, 1.00 no sub-grid, 1.00 max_Froude 1, 1.00 cfl 0.1,
    2.49 channel only >= 100 km2. With max_Froude 1 stored/rain never exceeds 1.00 in any full run.
    Results (town stage, BST): 2017 peak 13 Jun 16:30 (obs 13 Jun); 2023 7 Aug 22:30 (obs 7 Aug);
    2026 9 Jul 01:15 (obs 8 Jul, ~1 d late). Peak depth 14.70 / 14.24 / 14.08 m and 3 h Qout
    6,078 / 5,341 / 5,174 m3/s rank 2023 > 2017 > 2026, as observed (+283 / +135 / +96 cm over DL).
    Rank margins are small (0.6 m across the three against 1.9 m observed), and three events give a
    1-in-6 chance of the right order. Overbank duration ranks differently (2023 174 h > 2026 117 h >
    2017 51 h). Magnitudes are not credible (90 m DEM, no bathymetry): timing and rank only.
    Overlay, 2017 (62 landslides, all 13 Jun): median distance to a flooded valley (>= 0.5 m, >= 1 km2)
    360 m against 485 m for random catchment cells, within 1 km 97 % vs 87 %, Mann-Whitney p 0.061,
    on 14 one-km blocks p 0.45 -> NO detectable co-location at 90 m. Nearest-flood peak p10/50/90
    13 Jun 03:00 / 15:00 / 16:00, i.e. the valleys peaked hours after the first failures (02:30).
    No dated inventory landslides inside the catchment in the 2023 or 2026 windows.
    SENSITIVITY (lisflood_sensitivity.py -> results/lisflood_sensitivity.{csv,json}; one at a time,
    all three storms each, 8 variants + reference = 27 runs, stored/net rain <= 1.00 in all):
    floodplain n 0.03/0.08, channel n 0.025/0.05, infiltration 2/5 mm/h (infilfile), width
    coefficient 1.8/3.5. 2023 ranks highest in 9/9 configurations (depth and Qout). 2023 > 2017 >
    2026 in 7/9; the two high-roughness variants (floodplain 0.08, channel 0.05) give 2023 > 2026 >
    2017, with 2017 and 2026 within 0.1 m. Spread across storms 0.54-0.74 m, while one roughness
    step moves every storm by ~0.5 m. Peak on the recorded day: 2017 9/9; 2023 8/9 (floodplain 0.08:
    00:15 on 8 Aug); 2026 2/9 (only the low-roughness variants; else 01:15-02:30 on 9 Jul, i.e. a few
    hours past the recorded day). Infiltration and width barely matter (<= 0.3 m). Claim allowed:
    the model times the peaks and picks 2023 as the largest; it does NOT separate 2017 from 2026 ...... TIMING SOLID, 2023-LARGEST SOLID, 2017/2026 ORDER NOT RESOLVED, CO-LOCATION NULL
M11 GloFAS v5.0 check (fetch_glofas.py -> data/glofas/; glofas_check.py -> results/glofas_check.json,
    glofas_sangu.csv). Consolidated reanalysis, daily mean discharge (00-24 UTC), Jun-Sep 2001-2025 and
    Jun-Jul 2026, EWDS (CEMS-FLOODS licence accepted 2026-10-07). Sangu cell beside the FFWC station
    (22.175 N, 92.225 E; JJAS mean 156 m3/s, median annual max 544 m3/s). Peaks: 2017 365 m3/s on
    13 Jun (obs 13 Jun, offset 0; rank 18 of the 25 annual maxima); 2026 759 m3/s on 10 Jul (obs 8 Jul,
    +2 d; rank 5); 2023 207 m3/s on 10 Aug (obs 7 Aug, +3 d; lower than every annual maximum
    2001-2025). Order 2026 > 2017 > 2023, the reverse of the recorded stage (2023 > 2017 > 2026).
    Same order and offsets at all 14 cells of the Sangu chain in the box, so not a cell-choice
    artefact. Cause is the forcing: ERA5-Land rain at the station cell 1-10 Aug 2023 = 333 mm against
    856 mm gauged (NAWG); 2017 max day 96 mm against 332 mm; 2026 max day 89 mm against 309 mm. ERA5
    totals rank the storms 2026 (415 mm) > 2023 (333) > 2017 (230), and GloFAS follows its forcing.
    So GloFAS cannot arbitrate 2017 vs 2026: it misranks the event the record is clearest on. What it
    adds: a global system without a local rain anchor would have placed the worst of the three floods
    last, which supports anchoring rain to the station record (M10 rank holds for 2023 in 9/9
    configurations). Timing from GloFAS is right only for 2017 ...................... SOLID (as a negative result)
MERGE 2026-10-08: block M merged into the paper. Main text: Results 2.5 "What physical models add"
    (Sections/06b_models.tex; M2, M4, M6-M11; Fig. 6 = TRIGRS timing and 2026 replay), Methods
    "Physical and causal models" (Sections/02b_model_methods.tex), one sentence each in the
    abstract, Rangamati 2.3.2 and Limits, code availability. Supplement: Note 4 (flood model,
    GloFAS), Supplementary Fig. 1 (flood), Supplementary Table 2 (sensitivity). 17 references
    appended to references.bib. OPEN: modelling/ scripts not yet in the public repository (\todo in
    code availability); submission/ package not rebuilt while the paper is on hold.

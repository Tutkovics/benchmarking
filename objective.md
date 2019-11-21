# Felhő alapú alkalmazások teljesítményének kiértékelése és modellezése

A korszerű alkalmazások és hálózati szolgáltatások terhelésfüggő skálázhatóságának
alapja a virtualizáció és a felhők. Ebben a megközelítésben az alkalmazást Linux
konténerekbe telepített mikroszogáltatásokból építjük fel. Amennyiben a terhelés, például a
lekérdezések gyakorisága, megnő, úgy vagy megnöveljük az egyes konténerek számára
elérhető erőforrások mennyiségét („vertikális skálázás”) vagy több, egymás mellett futó
konténert indítunk el („horizontális skálázás”). Mindkét stratégia lehetővé teszi, hogy az
alkalmazás legfeljebb annyi erőforrást használjon a felhőben, amennyi a pillanatnyi terhelés
kiszolgálásához még pont elég. Ugyanakkor a két stratégia közötti választás nem mindig
egyszerű.

A jelölt feladata a felhőbe telepített alkalmazások terhelésfüggő erőforrásigényének
mérése és modellezése a horizontális és vertikális skálázási stratégiák közötti optimális
választás támogatásának céljából. Munkája terjedjen ki az alábbi feladatokra:
- Ismertesse Kubernetes konténer klaszter menedzsment rendszer felépítését, különös
tekintettel az alkalmazások számára elérhető erőforrások mennyiségének
konfigurálására és monitorozására, illetve a vertikális és horizontális skálázás
támogatására. Mutassa be egy egyszerű példán a két skálázási stratégiát.
- Válasszon 3–5 tipikus, kérdés-válasz típusú felhő alapú szolgáltatást (web szerver,
key-value store, autentikáció, naplózás, stb.) és végezze el az alkalmazások által
használt erőforrások terhelésfüggő mérését. A mérésekben pontosan szabályozza az
összterhelést, az egyes konténerek számára elérhető erőforrások maximális
mennyiségét, és a konténerek számát, és monitorozza az erőforrás-használatot (CPU
és memória) a fenti paraméterek függvényében.
- Keressen modellt, amellyel egyszerű profilok ismeretében a valós erőforrásfelhasználás pontosan megjósolható. (Ha ideje engedi, vizsgálja meg, hogy gépi
tanulási módszerekkel lehetséges-e pontosabb modelleket kapni.) Tesztelje a
modell(ek) pontosságát.
- Értékelje munkáját! Mikor működik jobban a vertikális skálázás és mikor a
horizontális? Léteznek az egyes alkalmazások specifikumaitól független, általános
szabályok?

Tanszéki konzulens: **Dr. Rétvári Gábor**

Budapest, 2019. 09. 26.
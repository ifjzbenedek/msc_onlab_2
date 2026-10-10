from src.pipeline.schemas.answer import Answer
from src.pipeline.schemas.citation import Citation

PLACEHOLDER_ANSWER = Answer(
    abstained=False,
    text=(
        "A vendéghallgatói kérelmet a regisztrációs időszak kezdete előtt legalább nyolc nappal kell "
        "benyújtanod, az Egyetem informatikai rendszerén keresztül, annak a karnak a Dékáni Hivatalához "
        "címezve, amelyiknek a kurzusait teljesíteni szeretnéd. Külföldi hallgatóként ez a határidő "
        "legfeljebb a szorgalmi időszak harmadik hetének végéig hosszabbítható meg. A kérelemről a Kari "
        "Tanulmányi Bizottság (KTB) dönt, az engedélyt pedig a kar Dékáni Hivatala adja ki a kérelem "
        "beérkezésétől számított nyolc napon belül."
    ),
    reliability="high",
    citations=[
        Citation(
            document="TVSZ",
            section="77. §",
            paragraph="(1)",
            text=(
                "(1) A vendéghallgatói jogviszony létesítésére vonatkozó kérelmet a regisztrációs időszak "
                "kezdete előtt legalább nyolc nappal kell benyújtani az Egyetem által működtetett "
                "informatikai rendszeren keresztül azon kar Dékáni Hivatalának címezve, amelyik kar "
                "kurzusait a kérelmező teljesíteni kívánja. Külföldi hallgató esetében e határidő "
                "legfeljebb a szorgalmi időszak harmadik hetének végéig meghosszabbítható. A kérelemről "
                "a KTB dönt."
            ),
        ),
        Citation(
            document="TVSZ",
            section="77. §",
            paragraph="(3)",
            text=(
                "(3) A kérelem alapján a vendéghallgatói jogviszony létesítésére vonatkozó engedélyt – a "
                "KTB döntése alapján – a kar Dékáni Hivatala adja ki a kérelem beérkezésétől számított "
                "nyolc napon belül. A határozatnak rendelkeznie kell vendéghallgató költségviselési "
                "formájáról, az esetlegesen fizetendő önköltség összegéről, fizetésének módjáról és "
                "határidejéről."
            ),
        ),
    ],
)

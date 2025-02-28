from typing import TypeAlias, Union

from Broken import BrokenEnum, install

install(package="kokoro_onnx[gpu]", pypi="kokoro-onnx")
install(package="misaki", pypi="misaki[ja,zh,en]")

# ------------------------------------------------------------------------------------------------ #

class _Speaker(BrokenEnum):

    @property
    def is_female(self) -> bool:
        return (self.value[1] == "f")

    @property
    def is_male(self) -> bool:
        return (self.value[1] == "m")

# ------------------------------------------------------------------------------------------------ #

class American(_Speaker):
    Alloy   = "af_alloy"
    Aoede   = "af_aoede"
    Bella   = "af_bella"
    Heart   = "af_heart"
    Jessica = "af_jessica"
    Kore    = "af_kore"
    Nicole  = "af_nicole"
    Nova    = "af_nova"
    River   = "af_river"
    Sarah   = "af_sarah"
    Sky     = "af_sky"
    Adam    = "am_adam"
    Echo    = "am_echo"
    Eric    = "am_eric"
    Fenrir  = "am_fenrir"
    Liam    = "am_liam"
    Michael = "am_michael"
    Onyx    = "am_onyx"
    Puck    = "am_puck"
    Santa   = "am_santa"

class British(_Speaker):
    Alice    = "bf_alice"
    Emma     = "bf_emma"
    Isabella = "bf_isabella"
    Lily     = "bf_lily"
    Daniel   = "bm_daniel"
    Fable    = "bm_fable"
    George   = "bm_george"
    Lewis    = "bm_lewis"

class Spanish(_Speaker):
    Dora  = "ef_dora"
    Alex  = "em_alex"
    Santa = "em_santa"

class French(_Speaker):
    FrenchSiwis = "ff_siwis"

class Hindi(_Speaker):
    HindiAlpha = "hf_alpha"
    HindiBeta  = "hf_beta"
    HindiOmega = "hm_omega"
    HindiPsi   = "hm_psi"

class Italian(_Speaker):
    Sara   = "if_sara"
    Nicola = "im_nicola"

class Japanese(_Speaker):
    Alpha      = "jf_alpha"
    Gongitsune = "jf_gongitsune"
    Nezumi     = "jf_nezumi"
    Tebukuro   = "jf_tebukuro"
    Kumo       = "jm_kumo"

class Portuguese(_Speaker):
    Dora  = "pf_dora"
    Alex  = "pm_alex"
    Santa = "pm_santa"

class Chinese(_Speaker):
    Xiaobei  = "zf_xiaobei"
    Xiaoni   = "zf_xiaoni"
    Xiaoxiao = "zf_xiaoxiao"
    Xiaoyi   = "zf_xiaoyi"
    Yunjian  = "zm_yunjian"
    Yunxi    = "zm_yunxi"
    Yunxia   = "zm_yunxia"
    Yunyang  = "zm_yunyang"

Speakers: TypeAlias = Union[
    American,
    British,
    Spanish,
    French,
    Hindi,
    Italian,
    Japanese,
    Portuguese,
    Chinese,
]

# ------------------------------------------------------------------------------------------------ #

# This name is so funny lol
class BrokenKokoro:
    ...


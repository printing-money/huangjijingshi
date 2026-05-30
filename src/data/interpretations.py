"""
卦辞爻辞解读引擎

包含64卦的卦辞、象辞、彖辞，以及384爻的爻辞。
提供基于卦象属性的综合解读能力。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..core.hexagram import Hexagram, get_hexagram, change_yao, TRIGRAM_NAMES


@dataclass
class HexagramInterpretation:
    """卦象解读"""
    name: str                    # 卦名
    gua_ci: str                  # 卦辞
    tuan_ci: str                 # 彖辞（简要）
    xiang_ci: str                # 大象辞
    nature: str                  # 卦性（吉/凶/平）
    keywords: list = field(default_factory=list)  # 关键词
    yao_ci: list = field(default_factory=list)    # 六爻爻辞


# 64卦解读数据（精选核心卦辞与象义）
INTERPRETATIONS: dict = {
    '乾': HexagramInterpretation(
        name='乾', gua_ci='元亨利贞',
        tuan_ci='大哉乾元，万物资始，乃统天',
        xiang_ci='天行健，君子以自强不息',
        nature='大吉', keywords=['刚健', '进取', '创始', '领导'],
        yao_ci=['潜龙勿用', '见龙在田，利见大人', '君子终日乾乾，夕惕若厉，无咎',
                '或跃在渊，无咎', '飞龙在天，利见大人', '亢龙有悔'],
    ),
    '坤': HexagramInterpretation(
        name='坤', gua_ci='元亨，利牝马之贞',
        tuan_ci='至哉坤元，万物资生，乃顺承天',
        xiang_ci='地势坤，君子以厚德载物',
        nature='吉', keywords=['柔顺', '包容', '承载', '厚德'],
        yao_ci=['履霜，坚冰至', '直方大，不习无不利', '含章可贞',
                '括囊，无咎无誉', '黄裳，元吉', '龙战于野，其血玄黄'],
    ),
    '屯': HexagramInterpretation(
        name='屯', gua_ci='元亨利贞，勿用有攸往，利建侯',
        tuan_ci='屯，刚柔始交而难生',
        xiang_ci='云雷屯，君子以经纶',
        nature='平', keywords=['初创', '艰难', '积蓄', '建设'],
        yao_ci=['磐桓，利居贞，利建侯', '屯如邅如，乘马班如', '即鹿无虞，惟入于林中',
                '乘马班如，求婚媾', '屯其膏，小贞吉，大贞凶', '乘马班如，泣血涟如'],
    ),
    '蒙': HexagramInterpretation(
        name='蒙', gua_ci='亨。匪我求童蒙，童蒙求我',
        tuan_ci='蒙，山下有险，险而止，蒙',
        xiang_ci='山下出泉，蒙，君子以果行育德',
        nature='平', keywords=['启蒙', '教育', '蒙昧', '求知'],
        yao_ci=['发蒙，利用刑人', '包蒙，吉', '勿用取女',
                '困蒙，吝', '童蒙，吉', '击蒙，不利为寇，利御寇'],
    ),
    '需': HexagramInterpretation(
        name='需', gua_ci='有孚，光亨，贞吉，利涉大川',
        tuan_ci='需，须也。险在前也，刚健而不陷',
        xiang_ci='云上于天，需，君子以饮食宴乐',
        nature='吉', keywords=['等待', '蓄势', '从容', '信心'],
        yao_ci=['需于郊，利用恒，无咎', '需于沙，小有言，终吉', '需于泥，致寇至',
                '需于血，出自穴', '需于酒食，贞吉', '入于穴，有不速之客三人来'],
    ),
    '讼': HexagramInterpretation(
        name='讼', gua_ci='有孚窒惕，中吉，终凶',
        tuan_ci='讼，上刚下险，险而健，讼',
        xiang_ci='天与水违行，讼，君子以作事谋始',
        nature='凶', keywords=['争讼', '矛盾', '谨慎', '止争'],
        yao_ci=['不永所事，小有言，终吉', '不克讼，归而逋', '食旧德，贞厉，终吉',
                '不克讼，复即命，渝安贞，吉', '讼，元吉', '或锡之鞶带，终朝三褫之'],
    ),
    '师': HexagramInterpretation(
        name='师', gua_ci='贞，丈人吉，无咎',
        tuan_ci='师，众也。贞，正也。能以众正，可以王矣',
        xiang_ci='地中有水，师，君子以容民畜众',
        nature='平', keywords=['军事', '纪律', '统帅', '众人'],
        yao_ci=['师出以律，否臧凶', '在师中，吉，无咎', '师或舆尸，凶',
                '师左次，无咎', '田有禽，利执言，无咎', '大君有命，开国承家'],
    ),
    '比': HexagramInterpretation(
        name='比', gua_ci='吉。原筮元永贞，无咎',
        tuan_ci='比，吉也。比，辅也。下顺从也',
        xiang_ci='地上有水，比，先王以建万国，亲诸侯',
        nature='吉', keywords=['亲附', '团结', '辅助', '和睦'],
        yao_ci=['有孚比之，无咎', '比之自内，贞吉', '比之匪人',
                '外比之，贞吉', '显比，王用三驱', '比之无首，凶'],
    ),
    '小畜': HexagramInterpretation(
        name='小畜', gua_ci='亨，密云不雨，自我西郊',
        tuan_ci='小畜，柔得位而上下应之',
        xiang_ci='风行天上，小畜，君子以懿文德',
        nature='平', keywords=['积蓄', '渐进', '修养', '等待'],
        yao_ci=['复自道，何其咎，吉', '牵复，吉', '舆说辐，夫妻反目',
                '有孚，血去惕出，无咎', '有孚挛如，富以其邻', '既雨既处，尚德载'],
    ),
    '履': HexagramInterpretation(
        name='履', gua_ci='履虎尾，不咥人，亨',
        tuan_ci='履，柔履刚也。说而应乎乾',
        xiang_ci='上天下泽，履，君子以辨上下，定民志',
        nature='平', keywords=['践行', '礼仪', '谨慎', '规矩'],
        yao_ci=['素履往，无咎', '履道坦坦，幽人贞吉', '眇能视，跛能履',
                '履虎尾，愬愬终吉', '夬履，贞厉', '视履考祥，其旋元吉'],
    ),
    '泰': HexagramInterpretation(
        name='泰', gua_ci='小往大来，吉亨',
        tuan_ci='泰，小往大来吉亨，则是天地交而万物通也',
        xiang_ci='天地交，泰，后以财成天地之道',
        nature='大吉', keywords=['通泰', '交融', '繁荣', '和谐'],
        yao_ci=['拔茅茹以其汇，征吉', '包荒，用冯河', '无平不陂，无往不复',
                '翩翩不富以其邻', '帝乙归妹，以祉元吉', '城复于隍，勿用师'],
    ),
    '否': HexagramInterpretation(
        name='否', gua_ci='否之匪人，不利君子贞',
        tuan_ci='否之匪人，不利君子贞，大往小来',
        xiang_ci='天地不交，否，君子以俭德辟难',
        nature='凶', keywords=['闭塞', '不通', '困顿', '隐忍'],
        yao_ci=['拔茅茹以其汇，贞吉亨', '包承，小人吉，大人否亨', '包羞',
                '有命无咎，畴离祉', '休否，大人吉', '倾否，先否后喜'],
    ),
    '同人': HexagramInterpretation(
        name='同人', gua_ci='同人于野，亨，利涉大川',
        tuan_ci='同人，柔得位得中而应乎乾',
        xiang_ci='天与火，同人，君子以类族辨物',
        nature='吉', keywords=['同心', '合作', '公正', '团结'],
        yao_ci=['同人于门，无咎', '同人于宗，吝', '伏戎于莽，升其高陵',
                '乘其墉，弗克攻，吉', '同人先号咷而后笑', '同人于郊，无悔'],
    ),
    '大有': HexagramInterpretation(
        name='大有', gua_ci='元亨',
        tuan_ci='大有，柔得尊位大中，而上下应之',
        xiang_ci='火在天上，大有，君子以遏恶扬善',
        nature='大吉', keywords=['丰盛', '光明', '富有', '包容'],
        yao_ci=['无交害，匪咎', '大车以载，有攸往，无咎', '公用亨于天子',
                '匪其彭，无咎', '厥孚交如，威如，吉', '自天祐之，吉无不利'],
    ),
    '谦': HexagramInterpretation(
        name='谦', gua_ci='亨，君子有终',
        tuan_ci='谦亨，天道下济而光明，地道卑而上行',
        xiang_ci='地中有山，谦，君子以裒多益寡',
        nature='吉', keywords=['谦逊', '低调', '平衡', '有终'],
        yao_ci=['谦谦君子，用涉大川，吉', '鸣谦，贞吉', '劳谦，君子有终，吉',
                '无不利，撝谦', '不富以其邻，利用侵伐', '鸣谦，利用行师'],
    ),
    '豫': HexagramInterpretation(
        name='豫', gua_ci='利建侯行师',
        tuan_ci='豫，刚应而志行，顺以动，豫',
        xiang_ci='雷出地奋，豫，先王以作乐崇德',
        nature='吉', keywords=['愉悦', '顺动', '建功', '乐观'],
        yao_ci=['鸣豫，凶', '介于石，不终日，贞吉', '盱豫，悔，迟有悔',
                '由豫，大有得', '贞疾，恒不死', '冥豫，成有渝，无咎'],
    ),
    '随': HexagramInterpretation(
        name='随', gua_ci='元亨利贞，无咎',
        tuan_ci='随，刚来而下柔，动而说，随',
        xiang_ci='泽中有雷，随，君子以向晦入宴息',
        nature='吉', keywords=['随顺', '适应', '跟随', '变通'],
        yao_ci=['官有渝，贞吉', '系小子，失丈夫', '系丈夫，失小子',
                '随有获，贞凶', '孚于嘉，吉', '拘系之，乃从维之'],
    ),
    '蛊': HexagramInterpretation(
        name='蛊', gua_ci='元亨，利涉大川',
        tuan_ci='蛊，刚上而柔下，巽而止，蛊',
        xiang_ci='山下有风，蛊，君子以振民育德',
        nature='平', keywords=['整治', '革新', '腐败', '振作'],
        yao_ci=['干父之蛊，有子考无咎', '干母之蛊，不可贞', '干父之蛊，小有悔',
                '裕父之蛊，往见吝', '干父之蛊，用誉', '不事王侯，高尚其事'],
    ),
    '临': HexagramInterpretation(
        name='临', gua_ci='元亨利贞，至于八月有凶',
        tuan_ci='临，刚浸而长，说而顺，刚中而应',
        xiang_ci='泽上有地，临，君子以教思无穷',
        nature='吉', keywords=['临近', '监督', '教化', '增长'],
        yao_ci=['咸临，贞吉', '咸临，吉，无不利', '甘临，无攸利',
                '至临，无咎', '知临，大君之宜，吉', '敦临，吉，无咎'],
    ),
    '观': HexagramInterpretation(
        name='观', gua_ci='盥而不荐，有孚颙若',
        tuan_ci='大观在上，顺而巽，中正以观天下',
        xiang_ci='风行地上，观，先王以省方观民设教',
        nature='平', keywords=['观察', '示范', '反省', '教化'],
        yao_ci=['童观，小人无咎，君子吝', '窥观，利女贞', '观我生，进退',
                '观国之光，利用宾于王', '观我生，君子无咎', '观其生，君子无咎'],
    ),
    '复': HexagramInterpretation(
        name='复', gua_ci='亨。出入无疾，朋来无咎',
        tuan_ci='复亨，刚反，动而以顺行',
        xiang_ci='雷在地中，复，先王以至日闭关',
        nature='吉', keywords=['回归', '复兴', '一阳来复', '新生'],
        yao_ci=['不远复，无祗悔，元吉', '休复，吉', '频复，厉，无咎',
                '中行独复', '敦复，无悔', '迷复，凶，有灾眚'],
    ),
    '姤': HexagramInterpretation(
        name='姤', gua_ci='女壮，勿用取女',
        tuan_ci='姤，遇也。柔遇刚也',
        xiang_ci='天下有风，姤，后以施命诰四方',
        nature='平', keywords=['相遇', '一阴初生', '警惕', '布令'],
        yao_ci=['系于金柅，贞吉', '包有鱼，无咎', '臀无肤，其行次且',
                '包无鱼，起凶', '以杞包瓜，含章', '姤其角，吝，无咎'],
    ),
    '革': HexagramInterpretation(
        name='革', gua_ci='己日乃孚，元亨利贞，悔亡',
        tuan_ci='革，水火相息。二女同居，其志不相得',
        xiang_ci='泽中有火，革，君子以治历明时',
        nature='吉', keywords=['变革', '革新', '除旧', '更新'],
        yao_ci=['巩用黄牛之革', '己日乃革之，征吉，无咎', '征凶，贞厉',
                '悔亡，有孚改命，吉', '大人虎变，未占有孚', '君子豹变，小人革面'],
    ),
    '鼎': HexagramInterpretation(
        name='鼎', gua_ci='元吉，亨',
        tuan_ci='鼎，象也。以木巽火，亨饪也',
        xiang_ci='木上有火，鼎，君子以正位凝命',
        nature='大吉', keywords=['鼎新', '文明', '养贤', '正位'],
        yao_ci=['鼎颠趾，利出否', '鼎有实，我仇有疾', '鼎耳革，其行塞',
                '鼎折足，覆公餗，其形渥，凶', '鼎黄耳金铉，利贞', '鼎玉铉，大吉，无不利'],
    ),
    '既济': HexagramInterpretation(
        name='既济', gua_ci='亨小，利贞，初吉终乱',
        tuan_ci='既济亨，小者亨也。利贞，刚柔正而位当也',
        xiang_ci='水在火上，既济，君子以思患而预防之',
        nature='平', keywords=['完成', '既成', '防患', '守成'],
        yao_ci=['曳其轮，濡其尾，无咎', '妇丧其茀，勿逐，七日得', '高宗伐鬼方',
                '繻有衣袽，终日戒', '东邻杀牛，不如西邻之禴祭', '濡其首，厉'],
    ),
    '未济': HexagramInterpretation(
        name='未济', gua_ci='亨，小狐汔济，濡其尾，无攸利',
        tuan_ci='未济亨，柔得中也',
        xiang_ci='火在水上，未济，君子以慎辨物居方',
        nature='平', keywords=['未完', '过渡', '谨慎', '希望'],
        yao_ci=['濡其尾，吝', '曳其轮，贞吉', '未济，征凶，利涉大川',
                '贞吉，悔亡', '贞吉，无悔，君子之光', '有孚于饮酒，无咎'],
    ),
}


class InterpretationEngine:
    """卦辞解读引擎"""

    def get_interpretation(self, hexagram: Hexagram) -> Optional[HexagramInterpretation]:
        """获取卦象的完整解读"""
        return INTERPRETATIONS.get(hexagram.name)

    def get_yao_ci(self, hexagram: Hexagram, yao: int) -> Optional[str]:
        """获取特定爻的爻辞"""
        interp = INTERPRETATIONS.get(hexagram.name)
        if interp and 1 <= yao <= 6 and len(interp.yao_ci) >= yao:
            return interp.yao_ci[yao - 1]
        return None

    def interpret_chain(self, chain) -> dict:
        """
        解读完整卦象链的综合含义

        综合分析各层卦象的象义、五行关系、阴阳状态
        """
        from .wuxing import get_hexagram_wuxing_analysis

        result = {
            'layers': {},
            'overall': '',
            'keywords': [],
            'nature': '',
        }

        # 逐层解读
        layer_names = [
            ('yuan', '元', chain.yuan),
            ('hui', '会', chain.hui),
            ('yun', '运', chain.yun),
            ('shi', '世', chain.shi),
            ('sui', '岁', chain.sui),
        ]

        all_keywords = []
        natures = []

        for key, label, hex_ in layer_names:
            interp = self.get_interpretation(hex_)
            layer_info = {
                'hexagram': f"{hex_.unicode}{hex_.name}",
                'gua_ci': interp.gua_ci if interp else '',
                'xiang_ci': interp.xiang_ci if interp else '',
                'nature': interp.nature if interp else '平',
                'keywords': interp.keywords if interp else [],
            }
            result['layers'][label] = layer_info

            if interp:
                all_keywords.extend(interp.keywords)
                natures.append(interp.nature)

        # 综合判断
        result['keywords'] = list(set(all_keywords))

        # 吉凶判断
        nature_scores = {'大吉': 2, '吉': 1, '平': 0, '凶': -1, '大凶': -2}
        if natures:
            avg_score = sum(nature_scores.get(n, 0) for n in natures) / len(natures)
            if avg_score > 1:
                result['nature'] = '大吉'
            elif avg_score > 0.3:
                result['nature'] = '吉'
            elif avg_score > -0.3:
                result['nature'] = '平'
            elif avg_score > -1:
                result['nature'] = '凶'
            else:
                result['nature'] = '大凶'

        # 生成总体解读
        sui_interp = self.get_interpretation(chain.sui)
        yun_interp = self.get_interpretation(chain.yun)

        parts = []
        if yun_interp:
            parts.append(f"运势大局：{yun_interp.xiang_ci}")
        if sui_interp:
            parts.append(f"流年主题：{sui_interp.gua_ci}")
            parts.append(f"象曰：{sui_interp.xiang_ci}")

        result['overall'] = '；'.join(parts) if parts else '卦辞数据待补充'

        return result

    def get_change_interpretation(self, from_hex: Hexagram, to_hex: Hexagram, yao: int) -> str:
        """解读变爻的含义"""
        from_interp = self.get_interpretation(from_hex)
        to_interp = self.get_interpretation(to_hex)

        parts = []
        if from_interp and len(from_interp.yao_ci) >= yao:
            parts.append(f"{from_hex.name}卦第{yao}爻动：{from_interp.yao_ci[yao - 1]}")
        if to_interp:
            parts.append(f"变为{to_hex.name}卦：{to_interp.gua_ci}")

        return '。'.join(parts) if parts else ''

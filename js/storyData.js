/**
 * KidsBook 3D Story Data
 * Featured Story: The Tale of Peter Rabbit by Beatrix Potter (1902)
 * Legal Status: 100% Public Domain worldwide (Zero copyright / IP restrictions)
 * Inspired by: Amazon Bestselling children's picture books (tactile, sensory, bedtime soothing)
 */

export const STORY_METADATA = {
  id: "peter_rabbit",
  title_en: "The Tale of Peter Rabbit",
  title_cn: "彼得兔的花园奇遇记",
  author_en: "Beatrix Potter",
  author_cn: "比阿特丽克斯·波特",
  published_year: 1902,
  copyright_status: "Public Domain (全球公有领域，无任何知识产权限制)",
  cover_image: "assets/renders/book_cover.png",
  total_chapters: 4
};

export const CHAPTERS = [
  {
    id: 1,
    title_en: "Chapter 1: The Fir Tree Burrow",
    title_cn: "第一章：巨型冷杉树下的温馨家",
    subtitle_en: "Under the roots of a giant fir tree",
    subtitle_cn: "粗大树根下的安睡之所",
    model: "assets/models/scene1_burrow.glb",
    preview: "assets/renders/chapter1_burrow.png",
    bg_gradient: "linear-gradient(135deg, #2c1e19 0%, #4a342a 50%, #211612 100%)",
    theme_color: "#b07d50",
    lighting: {
      ambient: 0.50,
      sun_intensity: 1.25,
      sun_color: 0xffeedd,
      warm_glow: 0xffaa44
    },
    text_en: "Once upon a time there were four little rabbits: Flopsy, Mopsy, Cotton-tail, and Peter. They lived with their Mother in a warm burrow under the roots of a very big fir-tree. 'Now my dears,' said old Mrs. Rabbit, 'you may go into the fields or down the lane, but don't go into Mr. McGregor's garden!'",
    text_cn: "从前有四只可爱的小兔子：弗洛普茜、莫普茜、棉球尾和彼得。他们和妈妈一起，住在一棵巨型冷杉树粗大树根下的温馨沙洞里。“亲爱的孩子们，”兔妈妈叮嘱道，“你们可以去田野里玩，或者沿着小径散步，但千万不要溜进麦格雷戈先生的菜园子里！”",
    audio_keywords: ["burrow", "rabbits", "Peter", "fir-tree", "Mother"],
    interactive_hints: [
      { id: "lantern", name_en: "Hanging Lantern", name_cn: "壁挂提灯", action: "toggle_glow" },
      { id: "teapot", name_en: "Herbal Teapot", name_cn: "陶瓷茶壶", action: "pour_tea" },
      { id: "rabbit", name_en: "Curious Peter", name_cn: "好奇的彼得", action: "wiggle_ears" }
    ]
  },
  {
    id: 2,
    title_en: "Chapter 2: Mr. McGregor's Garden",
    title_cn: "第二章：麦格雷戈先生的秘密菜园",
    subtitle_en: "Crisp lettuces and sweet orange carrots",
    subtitle_cn: "脆嫩的莴苣与甜甜的胡萝卜",
    model: "assets/models/scene2_garden.glb",
    preview: "assets/renders/chapter2_garden.png",
    bg_gradient: "linear-gradient(135deg, #1f3821 0%, #3e6833 50%, #2a4c28 100%)",
    theme_color: "#e67329",
    lighting: {
      ambient: 0.55,
      sun_intensity: 1.35,
      sun_color: 0xfffae8,
      warm_glow: 0x88cc44
    },
    text_en: "Peter did not listen! He squeezed right under the garden gate! First he ate some crisp lettuces and French beans, and then he pulled out delicious sweet carrots. But suddenly, round the end of a cucumber frame, whom should he meet but Mr. McGregor himself!",
    text_cn: "淘气的彼得才没有听话呢！他一下子就从菜园的大门缝底下钻了进去！他先是大口嚼着新鲜水灵的莴苣和扁豆，接着又拔出了甜滋滋的大胡萝卜。可就在他绕过黄瓜棚架拐角的一瞬间，迎面撞见的竟然就是麦格雷戈先生！",
    audio_keywords: ["Peter", "garden", "lettuces", "carrots", "McGregor"],
    interactive_hints: [
      { id: "carrot", name_en: "Sweet Carrots", name_cn: "多汁胡萝卜", action: "carrot_crunch" },
      { id: "watering_can", name_en: "Red Watering Can", name_cn: "红色喷水壶", action: "water_splash" },
      { id: "cabbage", name_en: "Crisp Cabbages", name_cn: "圆滚滚卷心菜", action: "bounce" }
    ]
  },
  {
    id: 3,
    title_en: "Chapter 3: The Gooseberry Netting",
    title_cn: "第三章：醋栗丛与遗落的蓝夹克",
    subtitle_en: "A narrow escape and a lost blue coat",
    subtitle_cn: "惊险脱险与挂在树枝上的纽扣",
    model: "assets/models/scene3_adventure.glb",
    preview: "assets/renders/chapter3_adventure.png",
    bg_gradient: "linear-gradient(135deg, #2c3328 0%, #465538 50%, #20271c 100%)",
    theme_color: "#2a62a8",
    lighting: {
      ambient: 0.50,
      sun_intensity: 1.25,
      sun_color: 0xffeed8,
      warm_glow: 0x4488ee
    },
    text_en: "Peter ran as fast as his little legs could carry him, but he ran straight into a gooseberry net! His brand-new blue jacket with large brass buttons caught tightly on the twigs. Peter shed big tears, but some friendly sparrows flew down, chirping: 'Don't give up, Peter! You can squeeze through!'",
    text_cn: "彼得撒腿就跑，小脚丫跑得飞快，却一头扎进了醋栗灌木丛的网里！他身上那件崭新的、闪耀着金色黄铜大纽扣的漂亮蓝夹克被树枝死死钩住了。彼得急得眼泪直打转，好在几只热心的小麻雀扑棱着翅膀飞过来鼓励他：“别放弃，彼得！用力挣脱出来！”",
    audio_keywords: ["Peter", "gooseberry", "jacket", "buttons", "sparrows"],
    interactive_hints: [
      { id: "jacket", name_en: "Trapped Blue Jacket", name_cn: "被挂住的蓝夹克", action: "sparkle_loose" },
      { id: "sparrow", name_en: "Friendly Bluebird", name_cn: "热心的小麻雀", action: "chirp" },
      { id: "wheelbarrow", name_en: "Garden Wheelbarrow", name_cn: "小木推车", action: "rattle" }
    ]
  },
  {
    id: 4,
    title_en: "Chapter 4: Safe at Home & Sweet Dreams",
    title_cn: "第四章：平安归家与温热洋甘菊茶",
    subtitle_en: "Warm blankets, moonlight, and peaceful dreams",
    subtitle_cn: "温暖被窝、柔美月光与香甜美梦",
    model: "assets/models/scene4_bedtime.glb",
    preview: "assets/renders/chapter4_bedtime.png",
    bg_gradient: "linear-gradient(135deg, #111424 0%, #1c223c 50%, #0d0f1c 100%)",
    theme_color: "#dca742",
    lighting: {
      ambient: 0.45,
      sun_intensity: 0.75,
      sun_color: 0x7799cc,
      warm_glow: 0xffaa33
    },
    text_en: "Peter never stopped until he reached the safety of the big fir-tree home. He was so tired that he flopped down on the soft bed. His gentle mother tucked him in with warm blankets and brewed a steaming cup of chamomile tea. 'One spoonful for good sleep!' whispered Mother, as Peter drifted into sweet, peaceful dreams.",
    text_cn: "彼得一刻也不敢停，一口气冲回了冷杉树下最安全的家里。他精疲力竭地倒在柔软温暖的小床上。温柔的兔妈妈给他盖上软乎乎的花布被子，端来了一杯热气腾腾的洋甘菊茶：“喝上一大勺，乖乖入睡吧。”窗外月光洒下，彼得在轻柔的晚风中进入了甜甜的梦乡。",
    audio_keywords: ["Peter", "fir-tree", "bed", "chamomile tea", "dreams"],
    interactive_hints: [
      { id: "tea", name_en: "Chamomile Tea", name_cn: "温热洋甘菊茶", action: "steam_swirl" },
      { id: "moon", name_en: "Crescent Moon", name_cn: "弯弯明月", action: "twinkle_stars" },
      { id: "bed", name_en: "Warm Blanket", name_cn: "暖烘烘小床", action: "sleep_sound" }
    ]
  }
];

export const OTHER_PUBLIC_DOMAIN_BOOKS = [
  {
    id: "little_prince",
    title_en: "The Little Prince (B-612)",
    title_cn: "小王子与星空玫瑰",
    author: "Antoine de Saint-Exupéry",
    year: 1943,
    tag: "Space / Philosophy",
    desc_en: "Asteroid B-612, the cherished rose, volcanic craters, and whimsical stars across the cosmos.",
    desc_cn: "小行星B-612、玻璃罩下的娇艳玫瑰、可爱的小火山与浩瀚的星空漫游。",
    status: "Public Domain / CC"
  },
  {
    id: "velveteen_rabbit",
    title_en: "The Velveteen Rabbit",
    title_cn: "绒布小兔子",
    author: "Margery Williams",
    year: 1922,
    tag: "Heartwarming Classic",
    desc_en: "A toy rabbit dreams of becoming 'Real' through the genuine love of a child.",
    desc_cn: "玩具小兔子在小男孩真挚的爱与呵护下，最终变成真正生命的神奇温情物语。",
    status: "Public Domain (1922)"
  },
  {
    id: "tortoise_hare",
    title_en: "The Tortoise and the Hare",
    title_cn: "龟兔赛跑",
    author: "Aesop's Fables",
    year: "Antiquity",
    tag: "Aesop / Moral Tale",
    desc_en: "The classic moral fable teaching perseverance and patience in a cheerful forest race.",
    desc_cn: "充满欢笑的森林运动会，寓教于乐地教会孩子们坚持不懈的古老伊索寓言。",
    status: "Public Domain"
  },
  {
    id: "three_pigs",
    title_en: "The Three Little Pigs",
    title_cn: "三只小猪建新房",
    author: "English Folk Tale",
    year: 1840,
    tag: "Fairy Tale",
    desc_en: "Straw, sticks, and solid red brick houses built to outsmart the huffing, puffing wolf.",
    desc_cn: "用稻草、木头与坚固红砖搭建房屋，机智勇敢抵御大灰狼的经典英国童话。",
    status: "Public Domain"
  }
];

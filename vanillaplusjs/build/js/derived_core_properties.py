EXACT_MATCHES_ID_START = frozenset(
    "\u00AA\u00B5\u00BA\u01BB\u0294\u02EC\u02EE\u0374\u037A\u037F\u0386\u038C\u0559\u0640\u06D5\u06FF\u0710\u07B1\u07FA\u081A\u0824\u0828\u08C9\u093D\u0950\u0971\u09B2\u09BD\u09CE\u09FC\u0A5E\u0ABD\u0AD0\u0AF9\u0B3D\u0B71\u0B83\u0B9C\u0BD0\u0C3D\u0C5D\u0C80\u0CBD\u0D3D\u0D4E\u0DBD\u0E46\u0E84\u0EA5\u0EBD\u0EC6\u0F00\u103F\u1061\u108E\u10C7\u10CD\u10FC\u1258\u12C0\u17D7\u17DC\u1843\u18AA\u1AA7\u1CFA\u1D78\u1F59\u1F5B\u1F5D\u1FBE\u2071\u207F\u2102\u2107\u2115\u2118\u2124\u2126\u2128\u212E\u2139\u214E\u2D27\u2D2D\u2D6F\u3005\u3006\u3007\u303B\u303C\u309F\u30FF\uA015\uA60C\uA66E\uA67F\uA770\uA788\uA78F\uA7D3\uA7F7\uA7FA\uA8FB\uA9CF\uA9E6\uAA70\uAA7A\uAAB1\uAAC0\uAAC2\uAADD\uAAF2\uAB69\uFB1D\uFB3E\uFF70\u10341\u1034A\u10808\u1083C\u10A00\u10F27\u11075\u11144\u11147\u11176\u111DA\u111DC\u11288\u1133D\u11350\u114C7\u11644\u116B8\u11909\u1193F\u11941\u119E1\u119E3\u11A00\u11A3A\u11A50\u11A9D\u11C40\u11D46\u11D98\u11FB0\u16F50\u16FE3\u1D4A2\u1D4BB\u1D546\u1DF0A\u1E14E\u1E94B\u1EE24\u1EE27\u1EE39\u1EE3B\u1EE42\u1EE47\u1EE49\u1EE4B\u1EE54\u1EE57\u1EE59\u1EE5B\u1EE5D\u1EE5F\u1EE64\u1EE7E"
)

MATCH_RANGES_ID_START = (
    (0x0041, 0x005A),
    (0x0061, 0x007A),
    (0x00C0, 0x00D6),
    (0x00D8, 0x00F6),
    (0x00F8, 0x01BA),
    (0x01BC, 0x01BF),
    (0x01C0, 0x01C3),
    (0x01C4, 0x0293),
    (0x0295, 0x02AF),
    (0x02B0, 0x02C1),
    (0x02C6, 0x02D1),
    (0x02E0, 0x02E4),
    (0x0370, 0x0373),
    (0x0376, 0x0377),
    (0x037B, 0x037D),
    (0x0388, 0x038A),
    (0x038E, 0x03A1),
    (0x03A3, 0x03F5),
    (0x03F7, 0x0481),
    (0x048A, 0x052F),
    (0x0531, 0x0556),
    (0x0560, 0x0588),
    (0x05D0, 0x05EA),
    (0x05EF, 0x05F2),
    (0x0620, 0x063F),
    (0x0641, 0x064A),
    (0x066E, 0x066F),
    (0x0671, 0x06D3),
    (0x06E5, 0x06E6),
    (0x06EE, 0x06EF),
    (0x06FA, 0x06FC),
    (0x0712, 0x072F),
    (0x074D, 0x07A5),
    (0x07CA, 0x07EA),
    (0x07F4, 0x07F5),
    (0x0800, 0x0815),
    (0x0840, 0x0858),
    (0x0860, 0x086A),
    (0x0870, 0x0887),
    (0x0889, 0x088E),
    (0x08A0, 0x08C8),
    (0x0904, 0x0939),
    (0x0958, 0x0961),
    (0x0972, 0x0980),
    (0x0985, 0x098C),
    (0x098F, 0x0990),
    (0x0993, 0x09A8),
    (0x09AA, 0x09B0),
    (0x09B6, 0x09B9),
    (0x09DC, 0x09DD),
    (0x09DF, 0x09E1),
    (0x09F0, 0x09F1),
    (0x0A05, 0x0A0A),
    (0x0A0F, 0x0A10),
    (0x0A13, 0x0A28),
    (0x0A2A, 0x0A30),
    (0x0A32, 0x0A33),
    (0x0A35, 0x0A36),
    (0x0A38, 0x0A39),
    (0x0A59, 0x0A5C),
    (0x0A72, 0x0A74),
    (0x0A85, 0x0A8D),
    (0x0A8F, 0x0A91),
    (0x0A93, 0x0AA8),
    (0x0AAA, 0x0AB0),
    (0x0AB2, 0x0AB3),
    (0x0AB5, 0x0AB9),
    (0x0AE0, 0x0AE1),
    (0x0B05, 0x0B0C),
    (0x0B0F, 0x0B10),
    (0x0B13, 0x0B28),
    (0x0B2A, 0x0B30),
    (0x0B32, 0x0B33),
    (0x0B35, 0x0B39),
    (0x0B5C, 0x0B5D),
    (0x0B5F, 0x0B61),
    (0x0B85, 0x0B8A),
    (0x0B8E, 0x0B90),
    (0x0B92, 0x0B95),
    (0x0B99, 0x0B9A),
    (0x0B9E, 0x0B9F),
    (0x0BA3, 0x0BA4),
    (0x0BA8, 0x0BAA),
    (0x0BAE, 0x0BB9),
    (0x0C05, 0x0C0C),
    (0x0C0E, 0x0C10),
    (0x0C12, 0x0C28),
    (0x0C2A, 0x0C39),
    (0x0C58, 0x0C5A),
    (0x0C60, 0x0C61),
    (0x0C85, 0x0C8C),
    (0x0C8E, 0x0C90),
    (0x0C92, 0x0CA8),
    (0x0CAA, 0x0CB3),
    (0x0CB5, 0x0CB9),
    (0x0CDD, 0x0CDE),
    (0x0CE0, 0x0CE1),
    (0x0CF1, 0x0CF2),
    (0x0D04, 0x0D0C),
    (0x0D0E, 0x0D10),
    (0x0D12, 0x0D3A),
    (0x0D54, 0x0D56),
    (0x0D5F, 0x0D61),
    (0x0D7A, 0x0D7F),
    (0x0D85, 0x0D96),
    (0x0D9A, 0x0DB1),
    (0x0DB3, 0x0DBB),
    (0x0DC0, 0x0DC6),
    (0x0E01, 0x0E30),
    (0x0E32, 0x0E33),
    (0x0E40, 0x0E45),
    (0x0E81, 0x0E82),
    (0x0E86, 0x0E8A),
    (0x0E8C, 0x0EA3),
    (0x0EA7, 0x0EB0),
    (0x0EB2, 0x0EB3),
    (0x0EC0, 0x0EC4),
    (0x0EDC, 0x0EDF),
    (0x0F40, 0x0F47),
    (0x0F49, 0x0F6C),
    (0x0F88, 0x0F8C),
    (0x1000, 0x102A),
    (0x1050, 0x1055),
    (0x105A, 0x105D),
    (0x1065, 0x1066),
    (0x106E, 0x1070),
    (0x1075, 0x1081),
    (0x10A0, 0x10C5),
    (0x10D0, 0x10FA),
    (0x10FD, 0x10FF),
    (0x1100, 0x1248),
    (0x124A, 0x124D),
    (0x1250, 0x1256),
    (0x125A, 0x125D),
    (0x1260, 0x1288),
    (0x128A, 0x128D),
    (0x1290, 0x12B0),
    (0x12B2, 0x12B5),
    (0x12B8, 0x12BE),
    (0x12C2, 0x12C5),
    (0x12C8, 0x12D6),
    (0x12D8, 0x1310),
    (0x1312, 0x1315),
    (0x1318, 0x135A),
    (0x1380, 0x138F),
    (0x13A0, 0x13F5),
    (0x13F8, 0x13FD),
    (0x1401, 0x166C),
    (0x166F, 0x167F),
    (0x1681, 0x169A),
    (0x16A0, 0x16EA),
    (0x16EE, 0x16F0),
    (0x16F1, 0x16F8),
    (0x1700, 0x1711),
    (0x171F, 0x1731),
    (0x1740, 0x1751),
    (0x1760, 0x176C),
    (0x176E, 0x1770),
    (0x1780, 0x17B3),
    (0x1820, 0x1842),
    (0x1844, 0x1878),
    (0x1880, 0x1884),
    (0x1885, 0x1886),
    (0x1887, 0x18A8),
    (0x18B0, 0x18F5),
    (0x1900, 0x191E),
    (0x1950, 0x196D),
    (0x1970, 0x1974),
    (0x1980, 0x19AB),
    (0x19B0, 0x19C9),
    (0x1A00, 0x1A16),
    (0x1A20, 0x1A54),
    (0x1B05, 0x1B33),
    (0x1B45, 0x1B4C),
    (0x1B83, 0x1BA0),
    (0x1BAE, 0x1BAF),
    (0x1BBA, 0x1BE5),
    (0x1C00, 0x1C23),
    (0x1C4D, 0x1C4F),
    (0x1C5A, 0x1C77),
    (0x1C78, 0x1C7D),
    (0x1C80, 0x1C88),
    (0x1C90, 0x1CBA),
    (0x1CBD, 0x1CBF),
    (0x1CE9, 0x1CEC),
    (0x1CEE, 0x1CF3),
    (0x1CF5, 0x1CF6),
    (0x1D00, 0x1D2B),
    (0x1D2C, 0x1D6A),
    (0x1D6B, 0x1D77),
    (0x1D79, 0x1D9A),
    (0x1D9B, 0x1DBF),
    (0x1E00, 0x1F15),
    (0x1F18, 0x1F1D),
    (0x1F20, 0x1F45),
    (0x1F48, 0x1F4D),
    (0x1F50, 0x1F57),
    (0x1F5F, 0x1F7D),
    (0x1F80, 0x1FB4),
    (0x1FB6, 0x1FBC),
    (0x1FC2, 0x1FC4),
    (0x1FC6, 0x1FCC),
    (0x1FD0, 0x1FD3),
    (0x1FD6, 0x1FDB),
    (0x1FE0, 0x1FEC),
    (0x1FF2, 0x1FF4),
    (0x1FF6, 0x1FFC),
    (0x2090, 0x209C),
    (0x210A, 0x2113),
    (0x2119, 0x211D),
    (0x212A, 0x212D),
    (0x212F, 0x2134),
    (0x2135, 0x2138),
    (0x213C, 0x213F),
    (0x2145, 0x2149),
    (0x2160, 0x2182),
    (0x2183, 0x2184),
    (0x2185, 0x2188),
    (0x2C00, 0x2C7B),
    (0x2C7C, 0x2C7D),
    (0x2C7E, 0x2CE4),
    (0x2CEB, 0x2CEE),
    (0x2CF2, 0x2CF3),
    (0x2D00, 0x2D25),
    (0x2D30, 0x2D67),
    (0x2D80, 0x2D96),
    (0x2DA0, 0x2DA6),
    (0x2DA8, 0x2DAE),
    (0x2DB0, 0x2DB6),
    (0x2DB8, 0x2DBE),
    (0x2DC0, 0x2DC6),
    (0x2DC8, 0x2DCE),
    (0x2DD0, 0x2DD6),
    (0x2DD8, 0x2DDE),
    (0x3021, 0x3029),
    (0x3031, 0x3035),
    (0x3038, 0x303A),
    (0x3041, 0x3096),
    (0x309B, 0x309C),
    (0x309D, 0x309E),
    (0x30A1, 0x30FA),
    (0x30FC, 0x30FE),
    (0x3105, 0x312F),
    (0x3131, 0x318E),
    (0x31A0, 0x31BF),
    (0x31F0, 0x31FF),
    (0x3400, 0x4DBF),
    (0x4E00, 0xA014),
    (0xA016, 0xA48C),
    (0xA4D0, 0xA4F7),
    (0xA4F8, 0xA4FD),
    (0xA500, 0xA60B),
    (0xA610, 0xA61F),
    (0xA62A, 0xA62B),
    (0xA640, 0xA66D),
    (0xA680, 0xA69B),
    (0xA69C, 0xA69D),
    (0xA6A0, 0xA6E5),
    (0xA6E6, 0xA6EF),
    (0xA717, 0xA71F),
    (0xA722, 0xA76F),
    (0xA771, 0xA787),
    (0xA78B, 0xA78E),
    (0xA790, 0xA7CA),
    (0xA7D0, 0xA7D1),
    (0xA7D5, 0xA7D9),
    (0xA7F2, 0xA7F4),
    (0xA7F5, 0xA7F6),
    (0xA7F8, 0xA7F9),
    (0xA7FB, 0xA801),
    (0xA803, 0xA805),
    (0xA807, 0xA80A),
    (0xA80C, 0xA822),
    (0xA840, 0xA873),
    (0xA882, 0xA8B3),
    (0xA8F2, 0xA8F7),
    (0xA8FD, 0xA8FE),
    (0xA90A, 0xA925),
    (0xA930, 0xA946),
    (0xA960, 0xA97C),
    (0xA984, 0xA9B2),
    (0xA9E0, 0xA9E4),
    (0xA9E7, 0xA9EF),
    (0xA9FA, 0xA9FE),
    (0xAA00, 0xAA28),
    (0xAA40, 0xAA42),
    (0xAA44, 0xAA4B),
    (0xAA60, 0xAA6F),
    (0xAA71, 0xAA76),
    (0xAA7E, 0xAAAF),
    (0xAAB5, 0xAAB6),
    (0xAAB9, 0xAABD),
    (0xAADB, 0xAADC),
    (0xAAE0, 0xAAEA),
    (0xAAF3, 0xAAF4),
    (0xAB01, 0xAB06),
    (0xAB09, 0xAB0E),
    (0xAB11, 0xAB16),
    (0xAB20, 0xAB26),
    (0xAB28, 0xAB2E),
    (0xAB30, 0xAB5A),
    (0xAB5C, 0xAB5F),
    (0xAB60, 0xAB68),
    (0xAB70, 0xABBF),
    (0xABC0, 0xABE2),
    (0xAC00, 0xD7A3),
    (0xD7B0, 0xD7C6),
    (0xD7CB, 0xD7FB),
    (0xF900, 0xFA6D),
    (0xFA70, 0xFAD9),
    (0xFB00, 0xFB06),
    (0xFB13, 0xFB17),
    (0xFB1F, 0xFB28),
    (0xFB2A, 0xFB36),
    (0xFB38, 0xFB3C),
    (0xFB40, 0xFB41),
    (0xFB43, 0xFB44),
    (0xFB46, 0xFBB1),
    (0xFBD3, 0xFD3D),
    (0xFD50, 0xFD8F),
    (0xFD92, 0xFDC7),
    (0xFDF0, 0xFDFB),
    (0xFE70, 0xFE74),
    (0xFE76, 0xFEFC),
    (0xFF21, 0xFF3A),
    (0xFF41, 0xFF5A),
    (0xFF66, 0xFF6F),
    (0xFF71, 0xFF9D),
    (0xFF9E, 0xFF9F),
    (0xFFA0, 0xFFBE),
    (0xFFC2, 0xFFC7),
    (0xFFCA, 0xFFCF),
    (0xFFD2, 0xFFD7),
    (0xFFDA, 0xFFDC),
    (0x10000, 0x1000B),
    (0x1000D, 0x10026),
    (0x10028, 0x1003A),
    (0x1003C, 0x1003D),
    (0x1003F, 0x1004D),
    (0x10050, 0x1005D),
    (0x10080, 0x100FA),
    (0x10140, 0x10174),
    (0x10280, 0x1029C),
    (0x102A0, 0x102D0),
    (0x10300, 0x1031F),
    (0x1032D, 0x10340),
    (0x10342, 0x10349),
    (0x10350, 0x10375),
    (0x10380, 0x1039D),
    (0x103A0, 0x103C3),
    (0x103C8, 0x103CF),
    (0x103D1, 0x103D5),
    (0x10400, 0x1044F),
    (0x10450, 0x1049D),
    (0x104B0, 0x104D3),
    (0x104D8, 0x104FB),
    (0x10500, 0x10527),
    (0x10530, 0x10563),
    (0x10570, 0x1057A),
    (0x1057C, 0x1058A),
    (0x1058C, 0x10592),
    (0x10594, 0x10595),
    (0x10597, 0x105A1),
    (0x105A3, 0x105B1),
    (0x105B3, 0x105B9),
    (0x105BB, 0x105BC),
    (0x10600, 0x10736),
    (0x10740, 0x10755),
    (0x10760, 0x10767),
    (0x10780, 0x10785),
    (0x10787, 0x107B0),
    (0x107B2, 0x107BA),
    (0x10800, 0x10805),
    (0x1080A, 0x10835),
    (0x10837, 0x10838),
    (0x1083F, 0x10855),
    (0x10860, 0x10876),
    (0x10880, 0x1089E),
    (0x108E0, 0x108F2),
    (0x108F4, 0x108F5),
    (0x10900, 0x10915),
    (0x10920, 0x10939),
    (0x10980, 0x109B7),
    (0x109BE, 0x109BF),
    (0x10A10, 0x10A13),
    (0x10A15, 0x10A17),
    (0x10A19, 0x10A35),
    (0x10A60, 0x10A7C),
    (0x10A80, 0x10A9C),
    (0x10AC0, 0x10AC7),
    (0x10AC9, 0x10AE4),
    (0x10B00, 0x10B35),
    (0x10B40, 0x10B55),
    (0x10B60, 0x10B72),
    (0x10B80, 0x10B91),
    (0x10C00, 0x10C48),
    (0x10C80, 0x10CB2),
    (0x10CC0, 0x10CF2),
    (0x10D00, 0x10D23),
    (0x10E80, 0x10EA9),
    (0x10EB0, 0x10EB1),
    (0x10F00, 0x10F1C),
    (0x10F30, 0x10F45),
    (0x10F70, 0x10F81),
    (0x10FB0, 0x10FC4),
    (0x10FE0, 0x10FF6),
    (0x11003, 0x11037),
    (0x11071, 0x11072),
    (0x11083, 0x110AF),
    (0x110D0, 0x110E8),
    (0x11103, 0x11126),
    (0x11150, 0x11172),
    (0x11183, 0x111B2),
    (0x111C1, 0x111C4),
    (0x11200, 0x11211),
    (0x11213, 0x1122B),
    (0x11280, 0x11286),
    (0x1128A, 0x1128D),
    (0x1128F, 0x1129D),
    (0x1129F, 0x112A8),
    (0x112B0, 0x112DE),
    (0x11305, 0x1130C),
    (0x1130F, 0x11310),
    (0x11313, 0x11328),
    (0x1132A, 0x11330),
    (0x11332, 0x11333),
    (0x11335, 0x11339),
    (0x1135D, 0x11361),
    (0x11400, 0x11434),
    (0x11447, 0x1144A),
    (0x1145F, 0x11461),
    (0x11480, 0x114AF),
    (0x114C4, 0x114C5),
    (0x11580, 0x115AE),
    (0x115D8, 0x115DB),
    (0x11600, 0x1162F),
    (0x11680, 0x116AA),
    (0x11700, 0x1171A),
    (0x11740, 0x11746),
    (0x11800, 0x1182B),
    (0x118A0, 0x118DF),
    (0x118FF, 0x11906),
    (0x1190C, 0x11913),
    (0x11915, 0x11916),
    (0x11918, 0x1192F),
    (0x119A0, 0x119A7),
    (0x119AA, 0x119D0),
    (0x11A0B, 0x11A32),
    (0x11A5C, 0x11A89),
    (0x11AB0, 0x11AF8),
    (0x11C00, 0x11C08),
    (0x11C0A, 0x11C2E),
    (0x11C72, 0x11C8F),
    (0x11D00, 0x11D06),
    (0x11D08, 0x11D09),
    (0x11D0B, 0x11D30),
    (0x11D60, 0x11D65),
    (0x11D67, 0x11D68),
    (0x11D6A, 0x11D89),
    (0x11EE0, 0x11EF2),
    (0x12000, 0x12399),
    (0x12400, 0x1246E),
    (0x12480, 0x12543),
    (0x12F90, 0x12FF0),
    (0x13000, 0x1342E),
    (0x14400, 0x14646),
    (0x16800, 0x16A38),
    (0x16A40, 0x16A5E),
    (0x16A70, 0x16ABE),
    (0x16AD0, 0x16AED),
    (0x16B00, 0x16B2F),
    (0x16B40, 0x16B43),
    (0x16B63, 0x16B77),
    (0x16B7D, 0x16B8F),
    (0x16E40, 0x16E7F),
    (0x16F00, 0x16F4A),
    (0x16F93, 0x16F9F),
    (0x16FE0, 0x16FE1),
    (0x17000, 0x187F7),
    (0x18800, 0x18CD5),
    (0x18D00, 0x18D08),
    (0x1AFF0, 0x1AFF3),
    (0x1AFF5, 0x1AFFB),
    (0x1AFFD, 0x1AFFE),
    (0x1B000, 0x1B122),
    (0x1B150, 0x1B152),
    (0x1B164, 0x1B167),
    (0x1B170, 0x1B2FB),
    (0x1BC00, 0x1BC6A),
    (0x1BC70, 0x1BC7C),
    (0x1BC80, 0x1BC88),
    (0x1BC90, 0x1BC99),
    (0x1D400, 0x1D454),
    (0x1D456, 0x1D49C),
    (0x1D49E, 0x1D49F),
    (0x1D4A5, 0x1D4A6),
    (0x1D4A9, 0x1D4AC),
    (0x1D4AE, 0x1D4B9),
    (0x1D4BD, 0x1D4C3),
    (0x1D4C5, 0x1D505),
    (0x1D507, 0x1D50A),
    (0x1D50D, 0x1D514),
    (0x1D516, 0x1D51C),
    (0x1D51E, 0x1D539),
    (0x1D53B, 0x1D53E),
    (0x1D540, 0x1D544),
    (0x1D54A, 0x1D550),
    (0x1D552, 0x1D6A5),
    (0x1D6A8, 0x1D6C0),
    (0x1D6C2, 0x1D6DA),
    (0x1D6DC, 0x1D6FA),
    (0x1D6FC, 0x1D714),
    (0x1D716, 0x1D734),
    (0x1D736, 0x1D74E),
    (0x1D750, 0x1D76E),
    (0x1D770, 0x1D788),
    (0x1D78A, 0x1D7A8),
    (0x1D7AA, 0x1D7C2),
    (0x1D7C4, 0x1D7CB),
    (0x1DF00, 0x1DF09),
    (0x1DF0B, 0x1DF1E),
    (0x1E100, 0x1E12C),
    (0x1E137, 0x1E13D),
    (0x1E290, 0x1E2AD),
    (0x1E2C0, 0x1E2EB),
    (0x1E7E0, 0x1E7E6),
    (0x1E7E8, 0x1E7EB),
    (0x1E7ED, 0x1E7EE),
    (0x1E7F0, 0x1E7FE),
    (0x1E800, 0x1E8C4),
    (0x1E900, 0x1E943),
    (0x1EE00, 0x1EE03),
    (0x1EE05, 0x1EE1F),
    (0x1EE21, 0x1EE22),
    (0x1EE29, 0x1EE32),
    (0x1EE34, 0x1EE37),
    (0x1EE4D, 0x1EE4F),
    (0x1EE51, 0x1EE52),
    (0x1EE61, 0x1EE62),
    (0x1EE67, 0x1EE6A),
    (0x1EE6C, 0x1EE72),
    (0x1EE74, 0x1EE77),
    (0x1EE79, 0x1EE7C),
    (0x1EE80, 0x1EE89),
    (0x1EE8B, 0x1EE9B),
    (0x1EEA1, 0x1EEA3),
    (0x1EEA5, 0x1EEA9),
    (0x1EEAB, 0x1EEBB),
    (0x20000, 0x2A6DF),
    (0x2A700, 0x2B738),
    (0x2B740, 0x2B81D),
    (0x2B820, 0x2CEA1),
    (0x2CEB0, 0x2EBE0),
    (0x2F800, 0x2FA1D),
    (0x30000, 0x3134A),
)

EXACT_MATCHES_ID_CONTINUE = frozenset(
    "\u005F\u00AA\u00B5\u00B7\u00BA\u01BB\u0294\u02EC\u02EE\u0374\u037A\u037F\u0386\u0387\u038C\u0559\u05BF\u05C7\u0640\u0670\u06D5\u06FF\u0710\u0711\u07B1\u07FA\u07FD\u081A\u0824\u0828\u08C9\u0903\u093A\u093B\u093C\u093D\u094D\u0950\u0971\u0981\u09B2\u09BC\u09BD\u09CD\u09CE\u09D7\u09FC\u09FE\u0A03\u0A3C\u0A51\u0A5E\u0A75\u0A83\u0ABC\u0ABD\u0AC9\u0ACD\u0AD0\u0AF9\u0B01\u0B3C\u0B3D\u0B3E\u0B3F\u0B40\u0B4D\u0B57\u0B71\u0B82\u0B83\u0B9C\u0BC0\u0BCD\u0BD0\u0BD7\u0C00\u0C04\u0C3C\u0C3D\u0C5D\u0C80\u0C81\u0CBC\u0CBD\u0CBE\u0CBF\u0CC6\u0D3D\u0D4D\u0D4E\u0D57\u0D81\u0DBD\u0DCA\u0DD6\u0E31\u0E46\u0E84\u0EA5\u0EB1\u0EBD\u0EC6\u0F00\u0F35\u0F37\u0F39\u0F7F\u0FC6\u1031\u1038\u103F\u1061\u1082\u108D\u108E\u108F\u109D\u10C7\u10CD\u10FC\u1258\u12C0\u1715\u1734\u17B6\u17C6\u17D7\u17DC\u17DD\u180F\u1843\u18A9\u18AA\u1932\u19DA\u1A1B\u1A55\u1A56\u1A57\u1A60\u1A61\u1A62\u1A7F\u1AA7\u1B04\u1B34\u1B35\u1B3B\u1B3C\u1B42\u1B82\u1BA1\u1BAA\u1BE6\u1BE7\u1BED\u1BEE\u1CE1\u1CED\u1CF4\u1CF7\u1CFA\u1D78\u1F59\u1F5B\u1F5D\u1FBE\u2054\u2071\u207F\u20E1\u2102\u2107\u2115\u2118\u2124\u2126\u2128\u212E\u2139\u214E\u2D27\u2D2D\u2D6F\u2D7F\u3005\u3006\u3007\u303B\u303C\u309F\u30FF\uA015\uA60C\uA66E\uA66F\uA67F\uA770\uA788\uA78F\uA7D3\uA7F7\uA7FA\uA802\uA806\uA80B\uA827\uA82C\uA8FB\uA8FF\uA983\uA9B3\uA9CF\uA9E5\uA9E6\uAA43\uAA4C\uAA4D\uAA70\uAA7A\uAA7B\uAA7C\uAA7D\uAAB0\uAAB1\uAAC0\uAAC1\uAAC2\uAADD\uAAEB\uAAF2\uAAF5\uAAF6\uAB69\uABE5\uABE8\uABEC\uABED\uFB1D\uFB1E\uFB3E\uFF3F\uFF70\u101FD\u102E0\u10341\u1034A\u10808\u1083C\u10A00\u10A3F\u10F27\u11000\u11001\u11002\u11070\u11075\u11082\u110C2\u1112C\u11144\u11147\u11173\u11176\u11182\u111CE\u111CF\u111DA\u111DC\u11234\u11235\u1123E\u11288\u112DF\u1133D\u11340\u11350\u11357\u11445\u11446\u1145E\u114B9\u114BA\u114C1\u114C7\u115BE\u1163D\u1163E\u11644\u116AB\u116AC\u116AD\u116B6\u116B7\u116B8\u11726\u11838\u11909\u1193D\u1193E\u1193F\u11940\u11941\u11942\u11943\u119E0\u119E1\u119E3\u119E4\u11A00\u11A39\u11A3A\u11A47\u11A50\u11A97\u11A9D\u11C2F\u11C3E\u11C3F\u11C40\u11CA9\u11CB1\u11CB4\u11D3A\u11D46\u11D47\u11D95\u11D96\u11D97\u11D98\u11FB0\u16F4F\u16F50\u16FE3\u16FE4\u1D4A2\u1D4BB\u1D546\u1DA75\u1DA84\u1DF0A\u1E14E\u1E2AE\u1E94B\u1EE24\u1EE27\u1EE39\u1EE3B\u1EE42\u1EE47\u1EE49\u1EE4B\u1EE54\u1EE57\u1EE59\u1EE5B\u1EE5D\u1EE5F\u1EE64\u1EE7E"
)

MATCH_RANGES_ID_CONTINUE = (
    (0x0030, 0x0039),
    (0x0041, 0x005A),
    (0x0061, 0x007A),
    (0x00C0, 0x00D6),
    (0x00D8, 0x00F6),
    (0x00F8, 0x01BA),
    (0x01BC, 0x01BF),
    (0x01C0, 0x01C3),
    (0x01C4, 0x0293),
    (0x0295, 0x02AF),
    (0x02B0, 0x02C1),
    (0x02C6, 0x02D1),
    (0x02E0, 0x02E4),
    (0x0300, 0x036F),
    (0x0370, 0x0373),
    (0x0376, 0x0377),
    (0x037B, 0x037D),
    (0x0388, 0x038A),
    (0x038E, 0x03A1),
    (0x03A3, 0x03F5),
    (0x03F7, 0x0481),
    (0x0483, 0x0487),
    (0x048A, 0x052F),
    (0x0531, 0x0556),
    (0x0560, 0x0588),
    (0x0591, 0x05BD),
    (0x05C1, 0x05C2),
    (0x05C4, 0x05C5),
    (0x05D0, 0x05EA),
    (0x05EF, 0x05F2),
    (0x0610, 0x061A),
    (0x0620, 0x063F),
    (0x0641, 0x064A),
    (0x064B, 0x065F),
    (0x0660, 0x0669),
    (0x066E, 0x066F),
    (0x0671, 0x06D3),
    (0x06D6, 0x06DC),
    (0x06DF, 0x06E4),
    (0x06E5, 0x06E6),
    (0x06E7, 0x06E8),
    (0x06EA, 0x06ED),
    (0x06EE, 0x06EF),
    (0x06F0, 0x06F9),
    (0x06FA, 0x06FC),
    (0x0712, 0x072F),
    (0x0730, 0x074A),
    (0x074D, 0x07A5),
    (0x07A6, 0x07B0),
    (0x07C0, 0x07C9),
    (0x07CA, 0x07EA),
    (0x07EB, 0x07F3),
    (0x07F4, 0x07F5),
    (0x0800, 0x0815),
    (0x0816, 0x0819),
    (0x081B, 0x0823),
    (0x0825, 0x0827),
    (0x0829, 0x082D),
    (0x0840, 0x0858),
    (0x0859, 0x085B),
    (0x0860, 0x086A),
    (0x0870, 0x0887),
    (0x0889, 0x088E),
    (0x0898, 0x089F),
    (0x08A0, 0x08C8),
    (0x08CA, 0x08E1),
    (0x08E3, 0x0902),
    (0x0904, 0x0939),
    (0x093E, 0x0940),
    (0x0941, 0x0948),
    (0x0949, 0x094C),
    (0x094E, 0x094F),
    (0x0951, 0x0957),
    (0x0958, 0x0961),
    (0x0962, 0x0963),
    (0x0966, 0x096F),
    (0x0972, 0x0980),
    (0x0982, 0x0983),
    (0x0985, 0x098C),
    (0x098F, 0x0990),
    (0x0993, 0x09A8),
    (0x09AA, 0x09B0),
    (0x09B6, 0x09B9),
    (0x09BE, 0x09C0),
    (0x09C1, 0x09C4),
    (0x09C7, 0x09C8),
    (0x09CB, 0x09CC),
    (0x09DC, 0x09DD),
    (0x09DF, 0x09E1),
    (0x09E2, 0x09E3),
    (0x09E6, 0x09EF),
    (0x09F0, 0x09F1),
    (0x0A01, 0x0A02),
    (0x0A05, 0x0A0A),
    (0x0A0F, 0x0A10),
    (0x0A13, 0x0A28),
    (0x0A2A, 0x0A30),
    (0x0A32, 0x0A33),
    (0x0A35, 0x0A36),
    (0x0A38, 0x0A39),
    (0x0A3E, 0x0A40),
    (0x0A41, 0x0A42),
    (0x0A47, 0x0A48),
    (0x0A4B, 0x0A4D),
    (0x0A59, 0x0A5C),
    (0x0A66, 0x0A6F),
    (0x0A70, 0x0A71),
    (0x0A72, 0x0A74),
    (0x0A81, 0x0A82),
    (0x0A85, 0x0A8D),
    (0x0A8F, 0x0A91),
    (0x0A93, 0x0AA8),
    (0x0AAA, 0x0AB0),
    (0x0AB2, 0x0AB3),
    (0x0AB5, 0x0AB9),
    (0x0ABE, 0x0AC0),
    (0x0AC1, 0x0AC5),
    (0x0AC7, 0x0AC8),
    (0x0ACB, 0x0ACC),
    (0x0AE0, 0x0AE1),
    (0x0AE2, 0x0AE3),
    (0x0AE6, 0x0AEF),
    (0x0AFA, 0x0AFF),
    (0x0B02, 0x0B03),
    (0x0B05, 0x0B0C),
    (0x0B0F, 0x0B10),
    (0x0B13, 0x0B28),
    (0x0B2A, 0x0B30),
    (0x0B32, 0x0B33),
    (0x0B35, 0x0B39),
    (0x0B41, 0x0B44),
    (0x0B47, 0x0B48),
    (0x0B4B, 0x0B4C),
    (0x0B55, 0x0B56),
    (0x0B5C, 0x0B5D),
    (0x0B5F, 0x0B61),
    (0x0B62, 0x0B63),
    (0x0B66, 0x0B6F),
    (0x0B85, 0x0B8A),
    (0x0B8E, 0x0B90),
    (0x0B92, 0x0B95),
    (0x0B99, 0x0B9A),
    (0x0B9E, 0x0B9F),
    (0x0BA3, 0x0BA4),
    (0x0BA8, 0x0BAA),
    (0x0BAE, 0x0BB9),
    (0x0BBE, 0x0BBF),
    (0x0BC1, 0x0BC2),
    (0x0BC6, 0x0BC8),
    (0x0BCA, 0x0BCC),
    (0x0BE6, 0x0BEF),
    (0x0C01, 0x0C03),
    (0x0C05, 0x0C0C),
    (0x0C0E, 0x0C10),
    (0x0C12, 0x0C28),
    (0x0C2A, 0x0C39),
    (0x0C3E, 0x0C40),
    (0x0C41, 0x0C44),
    (0x0C46, 0x0C48),
    (0x0C4A, 0x0C4D),
    (0x0C55, 0x0C56),
    (0x0C58, 0x0C5A),
    (0x0C60, 0x0C61),
    (0x0C62, 0x0C63),
    (0x0C66, 0x0C6F),
    (0x0C82, 0x0C83),
    (0x0C85, 0x0C8C),
    (0x0C8E, 0x0C90),
    (0x0C92, 0x0CA8),
    (0x0CAA, 0x0CB3),
    (0x0CB5, 0x0CB9),
    (0x0CC0, 0x0CC4),
    (0x0CC7, 0x0CC8),
    (0x0CCA, 0x0CCB),
    (0x0CCC, 0x0CCD),
    (0x0CD5, 0x0CD6),
    (0x0CDD, 0x0CDE),
    (0x0CE0, 0x0CE1),
    (0x0CE2, 0x0CE3),
    (0x0CE6, 0x0CEF),
    (0x0CF1, 0x0CF2),
    (0x0D00, 0x0D01),
    (0x0D02, 0x0D03),
    (0x0D04, 0x0D0C),
    (0x0D0E, 0x0D10),
    (0x0D12, 0x0D3A),
    (0x0D3B, 0x0D3C),
    (0x0D3E, 0x0D40),
    (0x0D41, 0x0D44),
    (0x0D46, 0x0D48),
    (0x0D4A, 0x0D4C),
    (0x0D54, 0x0D56),
    (0x0D5F, 0x0D61),
    (0x0D62, 0x0D63),
    (0x0D66, 0x0D6F),
    (0x0D7A, 0x0D7F),
    (0x0D82, 0x0D83),
    (0x0D85, 0x0D96),
    (0x0D9A, 0x0DB1),
    (0x0DB3, 0x0DBB),
    (0x0DC0, 0x0DC6),
    (0x0DCF, 0x0DD1),
    (0x0DD2, 0x0DD4),
    (0x0DD8, 0x0DDF),
    (0x0DE6, 0x0DEF),
    (0x0DF2, 0x0DF3),
    (0x0E01, 0x0E30),
    (0x0E32, 0x0E33),
    (0x0E34, 0x0E3A),
    (0x0E40, 0x0E45),
    (0x0E47, 0x0E4E),
    (0x0E50, 0x0E59),
    (0x0E81, 0x0E82),
    (0x0E86, 0x0E8A),
    (0x0E8C, 0x0EA3),
    (0x0EA7, 0x0EB0),
    (0x0EB2, 0x0EB3),
    (0x0EB4, 0x0EBC),
    (0x0EC0, 0x0EC4),
    (0x0EC8, 0x0ECD),
    (0x0ED0, 0x0ED9),
    (0x0EDC, 0x0EDF),
    (0x0F18, 0x0F19),
    (0x0F20, 0x0F29),
    (0x0F3E, 0x0F3F),
    (0x0F40, 0x0F47),
    (0x0F49, 0x0F6C),
    (0x0F71, 0x0F7E),
    (0x0F80, 0x0F84),
    (0x0F86, 0x0F87),
    (0x0F88, 0x0F8C),
    (0x0F8D, 0x0F97),
    (0x0F99, 0x0FBC),
    (0x1000, 0x102A),
    (0x102B, 0x102C),
    (0x102D, 0x1030),
    (0x1032, 0x1037),
    (0x1039, 0x103A),
    (0x103B, 0x103C),
    (0x103D, 0x103E),
    (0x1040, 0x1049),
    (0x1050, 0x1055),
    (0x1056, 0x1057),
    (0x1058, 0x1059),
    (0x105A, 0x105D),
    (0x105E, 0x1060),
    (0x1062, 0x1064),
    (0x1065, 0x1066),
    (0x1067, 0x106D),
    (0x106E, 0x1070),
    (0x1071, 0x1074),
    (0x1075, 0x1081),
    (0x1083, 0x1084),
    (0x1085, 0x1086),
    (0x1087, 0x108C),
    (0x1090, 0x1099),
    (0x109A, 0x109C),
    (0x10A0, 0x10C5),
    (0x10D0, 0x10FA),
    (0x10FD, 0x10FF),
    (0x1100, 0x1248),
    (0x124A, 0x124D),
    (0x1250, 0x1256),
    (0x125A, 0x125D),
    (0x1260, 0x1288),
    (0x128A, 0x128D),
    (0x1290, 0x12B0),
    (0x12B2, 0x12B5),
    (0x12B8, 0x12BE),
    (0x12C2, 0x12C5),
    (0x12C8, 0x12D6),
    (0x12D8, 0x1310),
    (0x1312, 0x1315),
    (0x1318, 0x135A),
    (0x135D, 0x135F),
    (0x1369, 0x1371),
    (0x1380, 0x138F),
    (0x13A0, 0x13F5),
    (0x13F8, 0x13FD),
    (0x1401, 0x166C),
    (0x166F, 0x167F),
    (0x1681, 0x169A),
    (0x16A0, 0x16EA),
    (0x16EE, 0x16F0),
    (0x16F1, 0x16F8),
    (0x1700, 0x1711),
    (0x1712, 0x1714),
    (0x171F, 0x1731),
    (0x1732, 0x1733),
    (0x1740, 0x1751),
    (0x1752, 0x1753),
    (0x1760, 0x176C),
    (0x176E, 0x1770),
    (0x1772, 0x1773),
    (0x1780, 0x17B3),
    (0x17B4, 0x17B5),
    (0x17B7, 0x17BD),
    (0x17BE, 0x17C5),
    (0x17C7, 0x17C8),
    (0x17C9, 0x17D3),
    (0x17E0, 0x17E9),
    (0x180B, 0x180D),
    (0x1810, 0x1819),
    (0x1820, 0x1842),
    (0x1844, 0x1878),
    (0x1880, 0x1884),
    (0x1885, 0x1886),
    (0x1887, 0x18A8),
    (0x18B0, 0x18F5),
    (0x1900, 0x191E),
    (0x1920, 0x1922),
    (0x1923, 0x1926),
    (0x1927, 0x1928),
    (0x1929, 0x192B),
    (0x1930, 0x1931),
    (0x1933, 0x1938),
    (0x1939, 0x193B),
    (0x1946, 0x194F),
    (0x1950, 0x196D),
    (0x1970, 0x1974),
    (0x1980, 0x19AB),
    (0x19B0, 0x19C9),
    (0x19D0, 0x19D9),
    (0x1A00, 0x1A16),
    (0x1A17, 0x1A18),
    (0x1A19, 0x1A1A),
    (0x1A20, 0x1A54),
    (0x1A58, 0x1A5E),
    (0x1A63, 0x1A64),
    (0x1A65, 0x1A6C),
    (0x1A6D, 0x1A72),
    (0x1A73, 0x1A7C),
    (0x1A80, 0x1A89),
    (0x1A90, 0x1A99),
    (0x1AB0, 0x1ABD),
    (0x1ABF, 0x1ACE),
    (0x1B00, 0x1B03),
    (0x1B05, 0x1B33),
    (0x1B36, 0x1B3A),
    (0x1B3D, 0x1B41),
    (0x1B43, 0x1B44),
    (0x1B45, 0x1B4C),
    (0x1B50, 0x1B59),
    (0x1B6B, 0x1B73),
    (0x1B80, 0x1B81),
    (0x1B83, 0x1BA0),
    (0x1BA2, 0x1BA5),
    (0x1BA6, 0x1BA7),
    (0x1BA8, 0x1BA9),
    (0x1BAB, 0x1BAD),
    (0x1BAE, 0x1BAF),
    (0x1BB0, 0x1BB9),
    (0x1BBA, 0x1BE5),
    (0x1BE8, 0x1BE9),
    (0x1BEA, 0x1BEC),
    (0x1BEF, 0x1BF1),
    (0x1BF2, 0x1BF3),
    (0x1C00, 0x1C23),
    (0x1C24, 0x1C2B),
    (0x1C2C, 0x1C33),
    (0x1C34, 0x1C35),
    (0x1C36, 0x1C37),
    (0x1C40, 0x1C49),
    (0x1C4D, 0x1C4F),
    (0x1C50, 0x1C59),
    (0x1C5A, 0x1C77),
    (0x1C78, 0x1C7D),
    (0x1C80, 0x1C88),
    (0x1C90, 0x1CBA),
    (0x1CBD, 0x1CBF),
    (0x1CD0, 0x1CD2),
    (0x1CD4, 0x1CE0),
    (0x1CE2, 0x1CE8),
    (0x1CE9, 0x1CEC),
    (0x1CEE, 0x1CF3),
    (0x1CF5, 0x1CF6),
    (0x1CF8, 0x1CF9),
    (0x1D00, 0x1D2B),
    (0x1D2C, 0x1D6A),
    (0x1D6B, 0x1D77),
    (0x1D79, 0x1D9A),
    (0x1D9B, 0x1DBF),
    (0x1DC0, 0x1DFF),
    (0x1E00, 0x1F15),
    (0x1F18, 0x1F1D),
    (0x1F20, 0x1F45),
    (0x1F48, 0x1F4D),
    (0x1F50, 0x1F57),
    (0x1F5F, 0x1F7D),
    (0x1F80, 0x1FB4),
    (0x1FB6, 0x1FBC),
    (0x1FC2, 0x1FC4),
    (0x1FC6, 0x1FCC),
    (0x1FD0, 0x1FD3),
    (0x1FD6, 0x1FDB),
    (0x1FE0, 0x1FEC),
    (0x1FF2, 0x1FF4),
    (0x1FF6, 0x1FFC),
    (0x203F, 0x2040),
    (0x2090, 0x209C),
    (0x20D0, 0x20DC),
    (0x20E5, 0x20F0),
    (0x210A, 0x2113),
    (0x2119, 0x211D),
    (0x212A, 0x212D),
    (0x212F, 0x2134),
    (0x2135, 0x2138),
    (0x213C, 0x213F),
    (0x2145, 0x2149),
    (0x2160, 0x2182),
    (0x2183, 0x2184),
    (0x2185, 0x2188),
    (0x2C00, 0x2C7B),
    (0x2C7C, 0x2C7D),
    (0x2C7E, 0x2CE4),
    (0x2CEB, 0x2CEE),
    (0x2CEF, 0x2CF1),
    (0x2CF2, 0x2CF3),
    (0x2D00, 0x2D25),
    (0x2D30, 0x2D67),
    (0x2D80, 0x2D96),
    (0x2DA0, 0x2DA6),
    (0x2DA8, 0x2DAE),
    (0x2DB0, 0x2DB6),
    (0x2DB8, 0x2DBE),
    (0x2DC0, 0x2DC6),
    (0x2DC8, 0x2DCE),
    (0x2DD0, 0x2DD6),
    (0x2DD8, 0x2DDE),
    (0x2DE0, 0x2DFF),
    (0x3021, 0x3029),
    (0x302A, 0x302D),
    (0x302E, 0x302F),
    (0x3031, 0x3035),
    (0x3038, 0x303A),
    (0x3041, 0x3096),
    (0x3099, 0x309A),
    (0x309B, 0x309C),
    (0x309D, 0x309E),
    (0x30A1, 0x30FA),
    (0x30FC, 0x30FE),
    (0x3105, 0x312F),
    (0x3131, 0x318E),
    (0x31A0, 0x31BF),
    (0x31F0, 0x31FF),
    (0x3400, 0x4DBF),
    (0x4E00, 0xA014),
    (0xA016, 0xA48C),
    (0xA4D0, 0xA4F7),
    (0xA4F8, 0xA4FD),
    (0xA500, 0xA60B),
    (0xA610, 0xA61F),
    (0xA620, 0xA629),
    (0xA62A, 0xA62B),
    (0xA640, 0xA66D),
    (0xA674, 0xA67D),
    (0xA680, 0xA69B),
    (0xA69C, 0xA69D),
    (0xA69E, 0xA69F),
    (0xA6A0, 0xA6E5),
    (0xA6E6, 0xA6EF),
    (0xA6F0, 0xA6F1),
    (0xA717, 0xA71F),
    (0xA722, 0xA76F),
    (0xA771, 0xA787),
    (0xA78B, 0xA78E),
    (0xA790, 0xA7CA),
    (0xA7D0, 0xA7D1),
    (0xA7D5, 0xA7D9),
    (0xA7F2, 0xA7F4),
    (0xA7F5, 0xA7F6),
    (0xA7F8, 0xA7F9),
    (0xA7FB, 0xA801),
    (0xA803, 0xA805),
    (0xA807, 0xA80A),
    (0xA80C, 0xA822),
    (0xA823, 0xA824),
    (0xA825, 0xA826),
    (0xA840, 0xA873),
    (0xA880, 0xA881),
    (0xA882, 0xA8B3),
    (0xA8B4, 0xA8C3),
    (0xA8C4, 0xA8C5),
    (0xA8D0, 0xA8D9),
    (0xA8E0, 0xA8F1),
    (0xA8F2, 0xA8F7),
    (0xA8FD, 0xA8FE),
    (0xA900, 0xA909),
    (0xA90A, 0xA925),
    (0xA926, 0xA92D),
    (0xA930, 0xA946),
    (0xA947, 0xA951),
    (0xA952, 0xA953),
    (0xA960, 0xA97C),
    (0xA980, 0xA982),
    (0xA984, 0xA9B2),
    (0xA9B4, 0xA9B5),
    (0xA9B6, 0xA9B9),
    (0xA9BA, 0xA9BB),
    (0xA9BC, 0xA9BD),
    (0xA9BE, 0xA9C0),
    (0xA9D0, 0xA9D9),
    (0xA9E0, 0xA9E4),
    (0xA9E7, 0xA9EF),
    (0xA9F0, 0xA9F9),
    (0xA9FA, 0xA9FE),
    (0xAA00, 0xAA28),
    (0xAA29, 0xAA2E),
    (0xAA2F, 0xAA30),
    (0xAA31, 0xAA32),
    (0xAA33, 0xAA34),
    (0xAA35, 0xAA36),
    (0xAA40, 0xAA42),
    (0xAA44, 0xAA4B),
    (0xAA50, 0xAA59),
    (0xAA60, 0xAA6F),
    (0xAA71, 0xAA76),
    (0xAA7E, 0xAAAF),
    (0xAAB2, 0xAAB4),
    (0xAAB5, 0xAAB6),
    (0xAAB7, 0xAAB8),
    (0xAAB9, 0xAABD),
    (0xAABE, 0xAABF),
    (0xAADB, 0xAADC),
    (0xAAE0, 0xAAEA),
    (0xAAEC, 0xAAED),
    (0xAAEE, 0xAAEF),
    (0xAAF3, 0xAAF4),
    (0xAB01, 0xAB06),
    (0xAB09, 0xAB0E),
    (0xAB11, 0xAB16),
    (0xAB20, 0xAB26),
    (0xAB28, 0xAB2E),
    (0xAB30, 0xAB5A),
    (0xAB5C, 0xAB5F),
    (0xAB60, 0xAB68),
    (0xAB70, 0xABBF),
    (0xABC0, 0xABE2),
    (0xABE3, 0xABE4),
    (0xABE6, 0xABE7),
    (0xABE9, 0xABEA),
    (0xABF0, 0xABF9),
    (0xAC00, 0xD7A3),
    (0xD7B0, 0xD7C6),
    (0xD7CB, 0xD7FB),
    (0xF900, 0xFA6D),
    (0xFA70, 0xFAD9),
    (0xFB00, 0xFB06),
    (0xFB13, 0xFB17),
    (0xFB1F, 0xFB28),
    (0xFB2A, 0xFB36),
    (0xFB38, 0xFB3C),
    (0xFB40, 0xFB41),
    (0xFB43, 0xFB44),
    (0xFB46, 0xFBB1),
    (0xFBD3, 0xFD3D),
    (0xFD50, 0xFD8F),
    (0xFD92, 0xFDC7),
    (0xFDF0, 0xFDFB),
    (0xFE00, 0xFE0F),
    (0xFE20, 0xFE2F),
    (0xFE33, 0xFE34),
    (0xFE4D, 0xFE4F),
    (0xFE70, 0xFE74),
    (0xFE76, 0xFEFC),
    (0xFF10, 0xFF19),
    (0xFF21, 0xFF3A),
    (0xFF41, 0xFF5A),
    (0xFF66, 0xFF6F),
    (0xFF71, 0xFF9D),
    (0xFF9E, 0xFF9F),
    (0xFFA0, 0xFFBE),
    (0xFFC2, 0xFFC7),
    (0xFFCA, 0xFFCF),
    (0xFFD2, 0xFFD7),
    (0xFFDA, 0xFFDC),
    (0x10000, 0x1000B),
    (0x1000D, 0x10026),
    (0x10028, 0x1003A),
    (0x1003C, 0x1003D),
    (0x1003F, 0x1004D),
    (0x10050, 0x1005D),
    (0x10080, 0x100FA),
    (0x10140, 0x10174),
    (0x10280, 0x1029C),
    (0x102A0, 0x102D0),
    (0x10300, 0x1031F),
    (0x1032D, 0x10340),
    (0x10342, 0x10349),
    (0x10350, 0x10375),
    (0x10376, 0x1037A),
    (0x10380, 0x1039D),
    (0x103A0, 0x103C3),
    (0x103C8, 0x103CF),
    (0x103D1, 0x103D5),
    (0x10400, 0x1044F),
    (0x10450, 0x1049D),
    (0x104A0, 0x104A9),
    (0x104B0, 0x104D3),
    (0x104D8, 0x104FB),
    (0x10500, 0x10527),
    (0x10530, 0x10563),
    (0x10570, 0x1057A),
    (0x1057C, 0x1058A),
    (0x1058C, 0x10592),
    (0x10594, 0x10595),
    (0x10597, 0x105A1),
    (0x105A3, 0x105B1),
    (0x105B3, 0x105B9),
    (0x105BB, 0x105BC),
    (0x10600, 0x10736),
    (0x10740, 0x10755),
    (0x10760, 0x10767),
    (0x10780, 0x10785),
    (0x10787, 0x107B0),
    (0x107B2, 0x107BA),
    (0x10800, 0x10805),
    (0x1080A, 0x10835),
    (0x10837, 0x10838),
    (0x1083F, 0x10855),
    (0x10860, 0x10876),
    (0x10880, 0x1089E),
    (0x108E0, 0x108F2),
    (0x108F4, 0x108F5),
    (0x10900, 0x10915),
    (0x10920, 0x10939),
    (0x10980, 0x109B7),
    (0x109BE, 0x109BF),
    (0x10A01, 0x10A03),
    (0x10A05, 0x10A06),
    (0x10A0C, 0x10A0F),
    (0x10A10, 0x10A13),
    (0x10A15, 0x10A17),
    (0x10A19, 0x10A35),
    (0x10A38, 0x10A3A),
    (0x10A60, 0x10A7C),
    (0x10A80, 0x10A9C),
    (0x10AC0, 0x10AC7),
    (0x10AC9, 0x10AE4),
    (0x10AE5, 0x10AE6),
    (0x10B00, 0x10B35),
    (0x10B40, 0x10B55),
    (0x10B60, 0x10B72),
    (0x10B80, 0x10B91),
    (0x10C00, 0x10C48),
    (0x10C80, 0x10CB2),
    (0x10CC0, 0x10CF2),
    (0x10D00, 0x10D23),
    (0x10D24, 0x10D27),
    (0x10D30, 0x10D39),
    (0x10E80, 0x10EA9),
    (0x10EAB, 0x10EAC),
    (0x10EB0, 0x10EB1),
    (0x10F00, 0x10F1C),
    (0x10F30, 0x10F45),
    (0x10F46, 0x10F50),
    (0x10F70, 0x10F81),
    (0x10F82, 0x10F85),
    (0x10FB0, 0x10FC4),
    (0x10FE0, 0x10FF6),
    (0x11003, 0x11037),
    (0x11038, 0x11046),
    (0x11066, 0x1106F),
    (0x11071, 0x11072),
    (0x11073, 0x11074),
    (0x1107F, 0x11081),
    (0x11083, 0x110AF),
    (0x110B0, 0x110B2),
    (0x110B3, 0x110B6),
    (0x110B7, 0x110B8),
    (0x110B9, 0x110BA),
    (0x110D0, 0x110E8),
    (0x110F0, 0x110F9),
    (0x11100, 0x11102),
    (0x11103, 0x11126),
    (0x11127, 0x1112B),
    (0x1112D, 0x11134),
    (0x11136, 0x1113F),
    (0x11145, 0x11146),
    (0x11150, 0x11172),
    (0x11180, 0x11181),
    (0x11183, 0x111B2),
    (0x111B3, 0x111B5),
    (0x111B6, 0x111BE),
    (0x111BF, 0x111C0),
    (0x111C1, 0x111C4),
    (0x111C9, 0x111CC),
    (0x111D0, 0x111D9),
    (0x11200, 0x11211),
    (0x11213, 0x1122B),
    (0x1122C, 0x1122E),
    (0x1122F, 0x11231),
    (0x11232, 0x11233),
    (0x11236, 0x11237),
    (0x11280, 0x11286),
    (0x1128A, 0x1128D),
    (0x1128F, 0x1129D),
    (0x1129F, 0x112A8),
    (0x112B0, 0x112DE),
    (0x112E0, 0x112E2),
    (0x112E3, 0x112EA),
    (0x112F0, 0x112F9),
    (0x11300, 0x11301),
    (0x11302, 0x11303),
    (0x11305, 0x1130C),
    (0x1130F, 0x11310),
    (0x11313, 0x11328),
    (0x1132A, 0x11330),
    (0x11332, 0x11333),
    (0x11335, 0x11339),
    (0x1133B, 0x1133C),
    (0x1133E, 0x1133F),
    (0x11341, 0x11344),
    (0x11347, 0x11348),
    (0x1134B, 0x1134D),
    (0x1135D, 0x11361),
    (0x11362, 0x11363),
    (0x11366, 0x1136C),
    (0x11370, 0x11374),
    (0x11400, 0x11434),
    (0x11435, 0x11437),
    (0x11438, 0x1143F),
    (0x11440, 0x11441),
    (0x11442, 0x11444),
    (0x11447, 0x1144A),
    (0x11450, 0x11459),
    (0x1145F, 0x11461),
    (0x11480, 0x114AF),
    (0x114B0, 0x114B2),
    (0x114B3, 0x114B8),
    (0x114BB, 0x114BE),
    (0x114BF, 0x114C0),
    (0x114C2, 0x114C3),
    (0x114C4, 0x114C5),
    (0x114D0, 0x114D9),
    (0x11580, 0x115AE),
    (0x115AF, 0x115B1),
    (0x115B2, 0x115B5),
    (0x115B8, 0x115BB),
    (0x115BC, 0x115BD),
    (0x115BF, 0x115C0),
    (0x115D8, 0x115DB),
    (0x115DC, 0x115DD),
    (0x11600, 0x1162F),
    (0x11630, 0x11632),
    (0x11633, 0x1163A),
    (0x1163B, 0x1163C),
    (0x1163F, 0x11640),
    (0x11650, 0x11659),
    (0x11680, 0x116AA),
    (0x116AE, 0x116AF),
    (0x116B0, 0x116B5),
    (0x116C0, 0x116C9),
    (0x11700, 0x1171A),
    (0x1171D, 0x1171F),
    (0x11720, 0x11721),
    (0x11722, 0x11725),
    (0x11727, 0x1172B),
    (0x11730, 0x11739),
    (0x11740, 0x11746),
    (0x11800, 0x1182B),
    (0x1182C, 0x1182E),
    (0x1182F, 0x11837),
    (0x11839, 0x1183A),
    (0x118A0, 0x118DF),
    (0x118E0, 0x118E9),
    (0x118FF, 0x11906),
    (0x1190C, 0x11913),
    (0x11915, 0x11916),
    (0x11918, 0x1192F),
    (0x11930, 0x11935),
    (0x11937, 0x11938),
    (0x1193B, 0x1193C),
    (0x11950, 0x11959),
    (0x119A0, 0x119A7),
    (0x119AA, 0x119D0),
    (0x119D1, 0x119D3),
    (0x119D4, 0x119D7),
    (0x119DA, 0x119DB),
    (0x119DC, 0x119DF),
    (0x11A01, 0x11A0A),
    (0x11A0B, 0x11A32),
    (0x11A33, 0x11A38),
    (0x11A3B, 0x11A3E),
    (0x11A51, 0x11A56),
    (0x11A57, 0x11A58),
    (0x11A59, 0x11A5B),
    (0x11A5C, 0x11A89),
    (0x11A8A, 0x11A96),
    (0x11A98, 0x11A99),
    (0x11AB0, 0x11AF8),
    (0x11C00, 0x11C08),
    (0x11C0A, 0x11C2E),
    (0x11C30, 0x11C36),
    (0x11C38, 0x11C3D),
    (0x11C50, 0x11C59),
    (0x11C72, 0x11C8F),
    (0x11C92, 0x11CA7),
    (0x11CAA, 0x11CB0),
    (0x11CB2, 0x11CB3),
    (0x11CB5, 0x11CB6),
    (0x11D00, 0x11D06),
    (0x11D08, 0x11D09),
    (0x11D0B, 0x11D30),
    (0x11D31, 0x11D36),
    (0x11D3C, 0x11D3D),
    (0x11D3F, 0x11D45),
    (0x11D50, 0x11D59),
    (0x11D60, 0x11D65),
    (0x11D67, 0x11D68),
    (0x11D6A, 0x11D89),
    (0x11D8A, 0x11D8E),
    (0x11D90, 0x11D91),
    (0x11D93, 0x11D94),
    (0x11DA0, 0x11DA9),
    (0x11EE0, 0x11EF2),
    (0x11EF3, 0x11EF4),
    (0x11EF5, 0x11EF6),
    (0x12000, 0x12399),
    (0x12400, 0x1246E),
    (0x12480, 0x12543),
    (0x12F90, 0x12FF0),
    (0x13000, 0x1342E),
    (0x14400, 0x14646),
    (0x16800, 0x16A38),
    (0x16A40, 0x16A5E),
    (0x16A60, 0x16A69),
    (0x16A70, 0x16ABE),
    (0x16AC0, 0x16AC9),
    (0x16AD0, 0x16AED),
    (0x16AF0, 0x16AF4),
    (0x16B00, 0x16B2F),
    (0x16B30, 0x16B36),
    (0x16B40, 0x16B43),
    (0x16B50, 0x16B59),
    (0x16B63, 0x16B77),
    (0x16B7D, 0x16B8F),
    (0x16E40, 0x16E7F),
    (0x16F00, 0x16F4A),
    (0x16F51, 0x16F87),
    (0x16F8F, 0x16F92),
    (0x16F93, 0x16F9F),
    (0x16FE0, 0x16FE1),
    (0x16FF0, 0x16FF1),
    (0x17000, 0x187F7),
    (0x18800, 0x18CD5),
    (0x18D00, 0x18D08),
    (0x1AFF0, 0x1AFF3),
    (0x1AFF5, 0x1AFFB),
    (0x1AFFD, 0x1AFFE),
    (0x1B000, 0x1B122),
    (0x1B150, 0x1B152),
    (0x1B164, 0x1B167),
    (0x1B170, 0x1B2FB),
    (0x1BC00, 0x1BC6A),
    (0x1BC70, 0x1BC7C),
    (0x1BC80, 0x1BC88),
    (0x1BC90, 0x1BC99),
    (0x1BC9D, 0x1BC9E),
    (0x1CF00, 0x1CF2D),
    (0x1CF30, 0x1CF46),
    (0x1D165, 0x1D166),
    (0x1D167, 0x1D169),
    (0x1D16D, 0x1D172),
    (0x1D17B, 0x1D182),
    (0x1D185, 0x1D18B),
    (0x1D1AA, 0x1D1AD),
    (0x1D242, 0x1D244),
    (0x1D400, 0x1D454),
    (0x1D456, 0x1D49C),
    (0x1D49E, 0x1D49F),
    (0x1D4A5, 0x1D4A6),
    (0x1D4A9, 0x1D4AC),
    (0x1D4AE, 0x1D4B9),
    (0x1D4BD, 0x1D4C3),
    (0x1D4C5, 0x1D505),
    (0x1D507, 0x1D50A),
    (0x1D50D, 0x1D514),
    (0x1D516, 0x1D51C),
    (0x1D51E, 0x1D539),
    (0x1D53B, 0x1D53E),
    (0x1D540, 0x1D544),
    (0x1D54A, 0x1D550),
    (0x1D552, 0x1D6A5),
    (0x1D6A8, 0x1D6C0),
    (0x1D6C2, 0x1D6DA),
    (0x1D6DC, 0x1D6FA),
    (0x1D6FC, 0x1D714),
    (0x1D716, 0x1D734),
    (0x1D736, 0x1D74E),
    (0x1D750, 0x1D76E),
    (0x1D770, 0x1D788),
    (0x1D78A, 0x1D7A8),
    (0x1D7AA, 0x1D7C2),
    (0x1D7C4, 0x1D7CB),
    (0x1D7CE, 0x1D7FF),
    (0x1DA00, 0x1DA36),
    (0x1DA3B, 0x1DA6C),
    (0x1DA9B, 0x1DA9F),
    (0x1DAA1, 0x1DAAF),
    (0x1DF00, 0x1DF09),
    (0x1DF0B, 0x1DF1E),
    (0x1E000, 0x1E006),
    (0x1E008, 0x1E018),
    (0x1E01B, 0x1E021),
    (0x1E023, 0x1E024),
    (0x1E026, 0x1E02A),
    (0x1E100, 0x1E12C),
    (0x1E130, 0x1E136),
    (0x1E137, 0x1E13D),
    (0x1E140, 0x1E149),
    (0x1E290, 0x1E2AD),
    (0x1E2C0, 0x1E2EB),
    (0x1E2EC, 0x1E2EF),
    (0x1E2F0, 0x1E2F9),
    (0x1E7E0, 0x1E7E6),
    (0x1E7E8, 0x1E7EB),
    (0x1E7ED, 0x1E7EE),
    (0x1E7F0, 0x1E7FE),
    (0x1E800, 0x1E8C4),
    (0x1E8D0, 0x1E8D6),
    (0x1E900, 0x1E943),
    (0x1E944, 0x1E94A),
    (0x1E950, 0x1E959),
    (0x1EE00, 0x1EE03),
    (0x1EE05, 0x1EE1F),
    (0x1EE21, 0x1EE22),
    (0x1EE29, 0x1EE32),
    (0x1EE34, 0x1EE37),
    (0x1EE4D, 0x1EE4F),
    (0x1EE51, 0x1EE52),
    (0x1EE61, 0x1EE62),
    (0x1EE67, 0x1EE6A),
    (0x1EE6C, 0x1EE72),
    (0x1EE74, 0x1EE77),
    (0x1EE79, 0x1EE7C),
    (0x1EE80, 0x1EE89),
    (0x1EE8B, 0x1EE9B),
    (0x1EEA1, 0x1EEA3),
    (0x1EEA5, 0x1EEA9),
    (0x1EEAB, 0x1EEBB),
    (0x1FBF0, 0x1FBF9),
    (0x20000, 0x2A6DF),
    (0x2A700, 0x2B738),
    (0x2B740, 0x2B81D),
    (0x2B820, 0x2CEA1),
    (0x2CEB0, 0x2EBE0),
    (0x2F800, 0x2FA1D),
    (0x30000, 0x3134A),
    (0xE0100, 0xE01EF),
)

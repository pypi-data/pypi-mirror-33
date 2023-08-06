import re

__all__ = ['讀trs']


def 讀trs(檔名):
    return _trs轉json.trs檔案(檔名)


class _trs轉json:

    @classmethod
    def trs檔案(cls, trs):
        with open(trs, encoding='utf-8') as 檔案:
            return cls.trs字串(檔案.read())

    @classmethod
    def trs字串(cls, trs):
        語者 = {}
        資料 = []
        這馬資料陣列 = []
        這馬時間 = None
        for 一逝 in trs.split('\n'):
            句 = 一逝.rstrip()
            if 句.startswith('<Speaker '):
                編號 = re.search(r' id="([^"]*)" ', 句).group(1)
                名 = re.search(r' name="([^"]*)" ', 句).group(1)
                語者[編號] = 名
            elif 句.startswith('<Turn '):
                try:
                    編號 = re.search(r' speaker="([^"]*)" ', 句).group(1)
                    這馬語者 = 語者[編號]
                except AttributeError:
                    這馬語者 = '無註明'
                結束時間 = re.search(r' endTime="([^"]*)"', 句).group(1)
            elif 句.startswith('</Turn>'):
                頂一个時間 = 這馬時間
                這馬時間 = 結束時間
                if cls._這馬敢有資料(這馬資料陣列):
                    if 頂一个時間 is None:
                        raise RuntimeError('trs有問題，無Sync時間煞有文本')
                    # 處理換逝的問題
                    資料.append({
                        '開始時間': 頂一个時間,
                        '結束時間': 這馬時間,
                        '語者': 這馬語者,
                        'trs聽拍': '\n'.join(這馬資料陣列).rstrip(),
                    })
                這馬資料陣列 = []
            elif 句.startswith('<Sync'):
                頂一个時間 = 這馬時間
                這馬時間 = 句.split('"')[1]
                if cls._這馬敢有資料(這馬資料陣列):
                    if 頂一个時間 is None:
                        raise RuntimeError(
                            'trs有問題，無Sync時間煞有文本，賰：{}'.format(這馬資料陣列)
                        )
                    資料.append({
                        '開始時間': 頂一个時間,
                        '結束時間': 這馬時間,
                        '語者': 這馬語者,
                        'trs聽拍': '\n'.join(這馬資料陣列).rstrip(),
                    })
                這馬資料陣列 = []
            elif (
                句.startswith('<?xml') or
                句.startswith('<!DOCTYPE') or
                句.startswith('<Trans') or
                句.startswith('</Trans') or
                句.startswith('<Speakers') or
                句.startswith('</Speakers') or
                句.startswith('<Topic') or
                句.startswith('</Topic') or
                句.startswith('<Episode') or
                句.startswith('</Episode') or
                句.startswith('<Section') or
                句.startswith('</Section') or
                句.startswith('<Episode')
            ):
                pass
            else:
                這馬資料陣列.append(句)
        if cls._這馬敢有資料(這馬資料陣列):
            raise RuntimeError('trs有問題，上尾的文本無Sync時間，賰：{}'.format(這馬資料陣列))
        return 資料

    @classmethod
    def _這馬敢有資料(cls, 這馬資料陣列):
        return len(''.join(這馬資料陣列).strip()) > 0

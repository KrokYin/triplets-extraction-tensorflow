#coding=utf-8
__author__ = 'Michael Hong'
import  json
import unicodedata
import nltk
import sys



def tag_sent(source_json, tag_json, isTrain=True):
    """
    Tagging the text based on the tagging tagging schema
    :param source_json: the sent text, entity mentions, relation mentions et.al
    :param tag_json: the sent text, the tag sequences, this program will generate this file
    :param isTrain:
    :return:
    """
    train_json_file = open(tag_json, 'w', 0)
    file = open(source_json, 'r')
    sentence = file.readlines()
    log_file = open('./data/log.txt', 'w', 0)
    article_num = 1
    for line in sentence:
        sent = json.loads(line.strip('\r\n'))
        sentText = sent['sentText']
        # process the encode problem of string
        sentText = str(unicodedata.normalize('NFKD', sentText).encode('ascii', 'ignore')).rstrip('\n').rstrip('\r')
        # obtain all words of sentText
        tokens = nltk.word_tokenize(sentText)
        tags = []
        for i in range(len(tokens)):
            tags.append('O')

        entityMentions = []
        entityByIndex = {}
        for em in sent['entityMentions']:
            # process the encode problem of string
            emText = unicodedata.normalize('NFKD', em['text']).encode('ascii', 'ignore')
            if emText not in entityByIndex:
                start, end = find_index(tokens, emText.split())
            else:
                offset = entityByIndex[emText][-1][1]
                start, end = find_index(tokens[offset:], emText.split())
                start += offset
                end += offset
            if start != -1 and end != -1:
                # invalid
                if end <= start:
                    continue
                if emText not in entityByIndex:
                    entityByIndex[emText] = [(start, end)]
                else:
                    entityByIndex[emText].append((start, end))

                entityMentions.append({'text': emText, 'start': start, 'end': end, 'label':em['label'].split(',')})

        visitedEntityMention = {}
        for rm in sent['relationMentions']:
            em1 = unicodedata.normalize('NFKD', rm['em1Text']).encode('ascii', 'ignore')
            em2 = unicodedata.normalize('NFKD', rm['em2Text']).encode('ascii', 'ignore')
            label = rm['label']
            # print label
            start1 = -1
            end1 = -1
            start2 = -1
            end2 = -1
            # it is different from train and test situation
            if isTrain:
                try:
                    start1, end1 = entityByIndex[em1][-1]
                    start2, end2 = entityByIndex[em2][-1]
                except KeyError:
                    a = 1
                    # print article_num, em1, em2
                    # sys.exit(0)
                    # log_file.write(str(article_num) + ' ' + em1 + ' ' + em2 + '\n')
            if start1 != -1 and end1 != -1 and start2 != -1 and end2 != -1:
                if ((start1, end1), (start2, end2)) not in visitedEntityMention:
                    visitedEntityMention[((start1, end1), (start2, end2))] = set([label])
                else:
                    visitedEntityMention[((start1, end1), (start2, end2))].add(label)

        #print visitedEntityMention
        if len(visitedEntityMention) > 0:
            # get the key
            for emPair in visitedEntityMention:
                valid = True
                for em1Pos in range(emPair[0][0], emPair[0][1]):
                    if not tags[em1Pos].__eq__('O'):
                        valid = False
                        break
                for em2Pos in range(emPair[1][0], emPair[1][1]):
                    if not tags[em2Pos].__eq__('O'):
                        valid = False
                        break
                if valid and non_overlab(emPair[0][0],emPair[0][1],emPair[1][0],emPair[1][1]):
                    for rmLabel in visitedEntityMention[emPair]:
                        if not rmLabel.__eq__('None'):
                            # print rmLabel
                            if emPair[0][1] - emPair[0][0] == 1:
                                tags[emPair[0][0]] = rmLabel + '__E1S'
                            elif emPair[0][1] - emPair[0][1] == 2:
                                tags[emPair[0][0]] = rmLabel + '__E1B'
                                tags[emPair[0][0] + 1] = rmLabel + '__E1L'
                            else:
                                tags[emPair[0][0]] = rmLabel + '__E1B'
                                tags[emPair[0][1] - 1] = rmLabel + '__E1L'
                                for ei in range(emPair[0][0] + 1, emPair[0][1] -1):
                                    tags[ei] = rmLabel + '__E1I'

                            if emPair[1][1] - emPair[1][0] == 1:
                                tags[emPair[1][0]] = rmLabel + '__E2S'
                            elif emPair[1][1] - emPair[1][0] == 2:
                                tags[emPair[1][0]] = rmLabel + '__E2B'
                                tags[emPair[1][0] + 1] = rmLabel + '__E2L'
                            else:
                                tags[emPair[1][0]] = rmLabel + '__E2B'
                                tags[emPair[1][1] - 1] = rmLabel + '__E2L'
                                for ei in range(emPair[1][0] + 1, emPair[1][1] - 1):
                                    tags[ei] = rmLabel + '__E2I'
                            break
        newsent = dict()
        newsent['tokens'] = tokens
        newsent['tags'] = tags
        train_json_file.write(json.dumps(newsent) + '\n')
        article_num += 1



def find_index(sen_split, tokens_split):
    """
    find the index of words in tokens_splits
    :param sen_split: source words
    :param tokens_split: target words
    :return: start_position, end_position, if it is not found ,then return (-1,-1)
    """
    start_position = -1
    end_position = -1
    for i in range(len(sen_split)):
        if str(sen_split[i]) == str(tokens_split[0]):
            k = i
            flag = True
            for j in range(len(tokens_split)):
                if sen_split[k] != tokens_split[j]:
                    flag = False
                if k < len(sen_split) - 1:
                    k += 1
            if flag:
                start_position = i
                end_position = i + len(tokens_split)
                break
    return start_position, end_position

def non_overlab(start1, end1, start2, end2):
    if start1 >= end2:
        return True
    if start2 >= end1:
        return True
    return False


if __name__ == '__main__':
    tag_sent('./data/demo/train.json', './data/demo/train_tag.json', isTrain=True)
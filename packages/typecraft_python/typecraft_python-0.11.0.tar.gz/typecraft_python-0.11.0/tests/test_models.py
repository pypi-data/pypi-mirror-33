import pytest
import six

from typecraft_python.core.models import Text, Phrase, Word, Morpheme, PhraseValidity, GlobalTag, GlobalTagSet, \
    DEFAULT_TAGSET


class TestModelsGeneral(object):

    def test_models_exist(self):
        assert Text is not None
        assert Phrase is not None
        assert Word is not None
        assert Morpheme is not None

    def test_to_dict(self):
        text = Text()
        phrase = Phrase()
        word = Word()
        morpheme = Morpheme()

        text.add_phrase(phrase)

        text_dict = text.to_dict()
        phrase_dict = phrase.to_dict()
        word_dict = word.to_dict()
        morpheme_dict = morpheme.to_dict()

        assert isinstance(text_dict, dict)
        assert isinstance(phrase_dict, dict)
        assert isinstance(word_dict, dict)
        assert isinstance(morpheme_dict, dict)

    def test_to_str(self):
        text = Text()
        phrase = Phrase()
        word = Word()
        morpheme = Morpheme()

        text.add_phrase(phrase)

        text_str = str(text)
        phrase_str = str(phrase)
        word_str = str(word)
        morpheme_str = str(morpheme)

        assert isinstance(text_str, six.string_types)
        assert isinstance(phrase_str, six.string_types)
        assert isinstance(word_str, six.string_types)
        assert isinstance(morpheme_str, six.string_types)


class TestText(object):

    def test_init(self):
        text = Text()

        assert text is not None
        assert text.title is ""
        assert text.title_translation is ""
        assert text.language is "und"
        assert text.plain_text is ""
        assert text.rich_text is ""
        assert text.metadata is not None
        assert text.phrases is not None

        phrase = Phrase()
        text2 = Text(
            title='Title',
            title_translation='Tittel',
            language='nob',
            plain_text='Dette er en tekst.',
            rich_text='<phrase>Dette er en tekst</phrase>',
            metadata={'key': 'value'},
            phrases=[phrase]
        )

        assert text2.title == 'Title'
        assert text2.title_translation == 'Tittel'
        assert text2.language == 'nob'
        assert text2.plain_text == 'Dette er en tekst.'
        assert text2.rich_text == '<phrase>Dette er en tekst</phrase>'
        assert text2.metadata == {'key': 'value'}
        assert phrase in text2.phrases

    def test_add_phrase_to_text(self):
        text = Text()

        phrase1 = Phrase()
        phrase2 = Phrase()

        text.add_phrase(phrase1)
        text.add_phrase(phrase2)

        assert phrase1 in text.phrases
        assert phrase2 in text.phrases

        text2 = Text()
        text2.add_phrases([phrase1, phrase2])

        assert phrase1 in text2.phrases
        assert phrase2 in text2.phrases

    def test_add_bad_phrase_to_text(self):
        text = Text()

        with pytest.raises(Exception):
            text.add_phrase("Arne")

        with pytest.raises(Exception):
            text.add_phrase({'phrase': 'phrase'})

        with pytest.raises(Exception):
            text.add_phrases([2, 52, ""])

    def test_iter_text(self):
        text = Text()

        phrase_1 = Phrase()
        phrase_2 = Phrase()

        phrases = [phrase_1, phrase_2]

        text.add_phrase(phrase_1)
        text.add_phrase(phrase_2)

        for phrase in text:
            assert phrase in phrases


class TestPhrase(object):

    def test_init(self):
        phrase = Phrase()

        assert phrase is not None

        assert phrase.phrase is ""
        assert phrase.translation is ""
        assert phrase.translation2 is ""
        assert phrase.comment is ""
        assert phrase.offset is 0
        assert phrase.duration is 0
        assert phrase.senses is not None
        assert phrase.words is not None

        word = Word()
        phrase2 = Phrase(
            phrase="Ola liker katter",
            translation="Ola likes cats",
            translation2="Ola s'aime chiennes",
            comment="Comment",
            offset=5,
            duration=0,
            words=[word]
        )

        assert phrase2.phrase == "Ola liker katter"
        assert phrase2.translation == "Ola likes cats"
        assert phrase2.translation2 == "Ola s'aime chiennes"
        assert phrase2.comment == "Comment"
        assert phrase2.offset == 5
        assert phrase2.duration == 0
        assert word in phrase2.words

    def test_init_phrase_with_validity_string(self):
        phrase = Phrase(validity='UNKNOWN')
        assert phrase.validity == PhraseValidity.UNKNOWN

    def test_add_word_to_phrase(self):
        phrase = Phrase()

        word1 = Word()
        word2 = Word()

        phrase.add_word(word1)
        phrase.add_word(word2)

        assert word1 in phrase
        assert word2 in phrase

        phrase2 = Phrase()

        phrase2.add_words([word1, word2])

        assert word1 in phrase2
        assert word2 in phrase2

    def test_add_bad_word_to_phrase(self):
        phrase = Phrase()

        with pytest.raises(Exception):
            phrase.add_word("Word")

        with pytest.raises(Exception):
            phrase.add_word({'word': 'Word'})

        with pytest.raises(Exception):
            phrase.add_word(2)

        with pytest.raises(Exception):
            phrase.add_words([2, 4, 5, ""])

    def test_iter_phrase(self):
        phrase = Phrase()

        word_1 = Word()
        word_2 = Word()

        words = [word_1, word_2]

        phrase.add_word(word_1)
        phrase.add_word(word_2)

        for word in phrase:
            assert word in words

    def test_phrase_add_global_tag(self):
        phrase = Phrase()
        phrase.add_global_tag(GlobalTag("name", 1, ""))

        assert len(phrase.global_tags) == 1
        assert phrase.global_tags[0].name == "name"
        assert phrase.global_tags[0].level == 1

    def test_phrase_add_global_tag_bad_argument_raises_exception(self):
        phrase = Phrase()

        with pytest.raises(Exception):
            phrase.add_global_tag("tag")
        with pytest.raises(Exception):
            phrase.add_global_tag(0)
        with pytest.raises(Exception):
            phrase.add_global_tag({'name': 'name', 'level': 1})
        with pytest.raises(Exception):
            phrase.add_global_tag(['name', 2])

    def test_phrase_add_global_tags(self):
        phrase = Phrase()
        phrase.add_global_tags([GlobalTag("name", 1, ""), GlobalTag("name2", 2, "")])

        assert len(phrase.global_tags) == 2
        assert phrase.global_tags[0].name == "name"
        assert phrase.global_tags[0].level == 1

        assert phrase.global_tags[1].name == "name2"
        assert phrase.global_tags[1].level == 2

    def test_phrase_add_global_tags_bad_argument_raises_exception(self):
        phrase = Phrase()

        with pytest.raises(Exception):
            phrase.add_global_tags(["name"])

        with pytest.raises(Exception):
            phrase.add_global_tags(["name"])

    def test_phrase_set_global_tagset(self):
        phrase = Phrase()

        phrase.set_global_tagset(GlobalTagSet(2, "Epic"))
        assert phrase.global_tag_set != DEFAULT_TAGSET
        assert phrase.global_tag_set.id == 2
        assert phrase.global_tag_set.name == "Epic"

    def test_phrase_has_default_tagset(self):
        phrase = Phrase()

        assert phrase.global_tag_set == DEFAULT_TAGSET


class TestWord(object):

    def test_init(self):
        word = Word()

        # Test defaults
        assert word.word == ""
        assert word.ipa == ""
        assert word.pos == ""
        assert word.stem_morpheme is None
        assert len(word.morphemes) == 0

        morpheme = Morpheme()
        word2 = Word(
            word="Ola",
            ipa="Ola",
            pos="N",
            stem_morpheme=morpheme,
            morphemes=[morpheme]
        )

        assert word2.word == "Ola"
        assert word2.ipa == "Ola"
        assert word2.pos == "N"
        assert word2.stem_morpheme == morpheme
        assert len(word2.morphemes) == 1
        assert morpheme in word2.morphemes

    def test_iter_word(self):
        word = Word()

        morph_1 = Morpheme()
        morph_2 = Morpheme()

        morphs = [morph_1, morph_2]

        word.add_morpheme(morph_1)
        word.add_morpheme(morph_2)

        for morph in word:
            assert morph in morphs

    def test_add_morpheme_to_word(self):
        word = Word()

        morpheme1 = Morpheme()
        morpheme2 = Morpheme()

        word.add_morpheme(morpheme1)
        word.add_morpheme(morpheme2)

        assert morpheme1 in word
        assert morpheme2 in word

        word2 = Word()
        word2.add_morphemes([morpheme1, morpheme2])
        assert morpheme1 in word2
        assert morpheme2 in word2

    def test_add_bad_morpheme_to_word(self):
        word = Word()

        with pytest.raises(Exception):
            word.add_morpheme("a")

        with pytest.raises(Exception):
            word.add_morpheme(2)

        with pytest.raises(Exception):
            word.add_morpheme({'morpheme': 'morpheme'})

        with pytest.raises(Exception):
            word.add_morphemes([2, 3, 'regerg'])


class TestMorpheme(object):

    def test_init_morpheme(self):
        morpheme = Morpheme()

        # Test defaults
        assert morpheme.morpheme == ""
        assert morpheme.meaning == ""
        assert morpheme.baseform == ""
        assert len(morpheme.glosses) == 0

        gloss = "SBJ"
        morpheme2 = Morpheme(
            morpheme="Ola",
            meaning="Ola",
            baseform="Ola",
            glosses=[gloss]
        )

        assert morpheme2.morpheme == "Ola"
        assert morpheme2.meaning == "Ola"
        assert morpheme2.baseform == "Ola"
        assert len(morpheme2.glosses) == 1
        assert "SBJ" in morpheme2.glosses

    def test_init_morpheme_concatenated_glosses(self):
        morpheme = Morpheme(
            glosses="SBJ.MOT"
        )

        assert "SBJ" in morpheme.glosses
        assert "MOT" in morpheme.glosses

    def test_get_glosses_concatenated(self):
        morpheme = Morpheme()

        morpheme.add_gloss("PURP")
        morpheme.add_gloss("ADJ>ADV")

        assert morpheme.get_glosses_concatenated() == "PURP.ADJ>ADV"
        assert morpheme.get_glosses_concatenated(sort=True) == "ADJ>ADV.PURP"

    def test_morpheme_add_concatenated_glosses(self):
        morpheme = Morpheme()

        morpheme.add_concatenated_glosses("SG.INDEF")
        assert 'SG' in morpheme.glosses
        assert 'INDEF' in morpheme.glosses

    def test_morpheme_add_concatenated_glosses_bad_input(self):
        morpheme = Morpheme()
        with pytest.raises(Exception):
            morpheme.add_concatenated_glosses([])
        with pytest.raises(Exception):
            morpheme.add_concatenated_glosses({})
        class SomeClass:
            pass
        with pytest.raises(Exception):
            morpheme.add_concatenated_glosses(SomeClass())
        with pytest.raises(Exception):
            morpheme.add_concatenated_glosses(2)
        with pytest.raises(Exception):
            morpheme.add_concatenated_glosses(5)

    def test_morpheme_add_concatenated_glosses_single_input(self):
        """
        The method should also handle a 'single' gloss string
        """
        morpheme = Morpheme()
        morpheme.add_concatenated_glosses('SG')

        assert 'SG' in morpheme.glosses





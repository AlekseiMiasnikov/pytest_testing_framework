from random import choice

from allure import title, description, suite, parent_suite

from core.utils.testrail import TestRail


@parent_suite('[Pytest][UI][MOBILE]')
@suite('Mobile')
class TestMobile:
    @TestRail.suite('UI: Geekbench')
    @title('Поиск текста в Geekbench')
    @description('Поиск текста "Running JPEG" на 3% загрузки. Android: Geekbench')
    @TestRail.id('id_test_case')
    def test_android_geekbench(self, main_screen_geekbench):
        main_screen_geekbench.click_by_id(idx='android:id/button1')
        main_screen_geekbench.click_by_id(idx='com.primatelabs.geekbench:id/runCpuBenchmarks')
        main_screen_geekbench.assert_text(
            idx='android:id/alertTitle',
            text='Geekbench 4'
        )
        main_screen_geekbench.smart_assert_text(
            idx='android:id/message',
            text='Running JPEG'
        )

    @TestRail.suite('UI: Notepad')
    @title('Создание записей и проверка наличия записи Notepad')
    @description('Создание трёх записей с последующим случайным поиском одной из созданных записей. Android: Notepad')
    @TestRail.id('id_test_case')
    def test_android_notepad(self, main_screen_notepad):
        notes_records = ['python', 'pytest', 'appium']
        for item in notes_records:
            main_screen_notepad.click_by_id(idx='com.notes.notepad:id/fab')
            main_screen_notepad.click_by_id(idx='com.notes.notepad:id/scrollView2')
            main_screen_notepad.set_value(
                set_type='id',
                element='com.notes.notepad:id/editText',
                text=item
            )
            main_screen_notepad.click_by_class(class_name='android.widget.ImageButton')
        main_screen_notepad.click_by_id(idx='com.notes.notepad:id/action_search')
        record = choice(notes_records)
        main_screen_notepad.set_value(
            set_type='class',
            element='android.widget.EditText',
            text=record
        )
        main_screen_notepad.click_by_id(idx='android:id/button1')
        main_screen_notepad.assert_text(
            idx='com.notes.notepad:id/text1',
            text=record
        )

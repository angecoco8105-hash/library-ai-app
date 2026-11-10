
import os
import io
from contextlib import redirect_stdout

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from datetime import date, timedelta

books = []
members = []
borrow_records = []

def add_book(book_id, title, author, copies):
    for book in books:
        if book["book_id"] == book_id:
            print(f"図書ID「{book_id}」の本は既に存在します。")
            return

    books.append({"book_id": book_id, "title": title, "author": author, "copies": copies, "available_copies": copies})
    print(f"図書「{title}」（ID: {book_id}, 著者: {author}, 冊数: {copies}）を追加しました。")

def list_books():
    if not books:
        print("現在、登録されている図書はありません。")
        return

    print("--- 図書一覧 ---")
    for book in books:
        print(f"ID: {book['book_id']}, タイトル: {book['title']}, 著者: {book['author']}, 総冊数: {book['copies']}, 在庫: {book['available_copies']}")

def search_book(book_id):
    for book in books:
        if book["book_id"] == book_id:
            print(f"ID: {book['book_id']}, タイトル: {book['title']}, 著者: {book['author']}, 総冊数: {book['copies']}, 在庫: {book['available_copies']}")
            return
    print(f"図書ID「{book_id}」の本は存在しません。")

def add_member(member_id, name):
    for member in members:
        if member["member_id"] == member_id:
            print(f"会員ID「{member_id}」の会員は既に存在します。")
            return

    members.append({"member_id": member_id, "name": name})
    print(f"会員「{name}」（ID: {member_id}）を追加しました。")

def list_members():
    if not members:
        print("現在、登録されている会員はいません。")
        return

    print("--- 会員一覧 ---")
    for member in members:
        print(f"ID: {member['member_id']}, 名前: {member['name']}")

def borrow_book(book_id, member_id):
    book = ""
    for b in books:
        if b["book_id"] == book_id:
            book = b
            break
    if not book:
        print(f"図書ID「{book_id}」の本は存在しません。")
        return

    member = ""
    for m in members:
        if m["member_id"] == member_id:
            member = m
            break
    if not member:
        print(f"会員ID「{member_id}」の会員は存在しません。")
        return

    if book["available_copies"] <= 0:
        print(f"図書「{book['title']}」は現在貸出可能な冊数がありません。")
        return

    
    record_count = 0
    for record in borrow_records:
     if (
            member["member_id"] == record["member_id"]
            and not record["returned"]
        ):
            record_count += 1

    if record_count == 5:
        print(f"貸出可能数は5冊までです。")
        return

    today = date.today()
    due_date = today + timedelta(days=7)

    borrow_records.append({
        "book_id": book_id,
        "member_id": member_id,
        "borrow_date": today.isoformat(),
        "due_date": due_date.isoformat(),
        "returned": False
    })

    print(
        f"図書「{book['title']}」を"
        f"会員「{member['name']}」に貸し出しました。\n"
        f"返却期限: {due_date.isoformat()}"
    )

    book["available_copies"] -= 1


def list_borrowed_books():
    print("--- 貸出中の図書一覧 ---")
    borrow_count = 0
    for record in borrow_records:
        if not record["returned"]:
            book = ""
            for b in books:
                if b["book_id"] == record["book_id"]:
                    book = b
            member = ""
            for m in members:
                if m["member_id"] == record["member_id"]:
                    member = m
            print(f"図書: {book['title']}（ID: {record['book_id']}）, 会員: {member['name']}（ID: {record['member_id']}）, 貸出日: {record['borrow_date']}, 返却期限: {record['due_date']}")
            borrow_count += 1
    if borrow_count == 0:
        print("現在、貸出中の図書はありません。")

def return_book(book_id, member_id):
    record = ""
    for r in borrow_records:
        if r["book_id"] == book_id and r["member_id"] == member_id and not r["returned"]:
            r["returned"] = True
            record = r
            break
    if not record:
        print(f"図書ID「{book_id}」本を会員ID「{member_id}」の会員は借りていません。")
        return

    book = ""
    for b in books:
        if b["book_id"] == book_id:
            b["available_copies"] += 1
            book = b
            break

    if not book:
        print(f"図書ID「{book['book_id']}」の本は存在しません。")
        return
    print(f"図書「{book['title']}」が返却されました。")


def calculate_fines():
    print("--- 延滞料金一覧 ---")
    borrow_count = 0

    for record in borrow_records:
        if not record["returned"]:
            borrow_count += 1

            book = ""
            for b in books:
                if b["book_id"] == record["book_id"]:
                    book = b
                    break

            member = ""
            for m in members:
                if m["member_id"] == record["member_id"]:
                    member = m
                    break

            due_date = date.fromisoformat(record["due_date"])
            today = date.today()

            overdue_days = max((today - due_date).days, 0)
            fine = overdue_days * 100

            print(
                f"図書: {book['title']}（ID: {record['book_id']}）, "
                f"会員: {member['name']}（ID: {record['member_id']}）, "
                f"延滞日数: {overdue_days}日, "
                f"延滞料金: {fine}円"
            )

    if borrow_count == 0:
        print("現在、貸出中の図書はありません。")


def main():
    while True:
        print("図書館管理システムメニュー:")
        print("1: 図書を追加")
        print("2: 図書一覧を表示")
        print("3: 図書を検索")
        print("4: 会員を追加")
        print("5: 会員一覧を表示")
        print("6: 図書を貸し出す")
        print("7: 貸出中の図書一覧を表示")
        print("8: 図書を返却")
        print("9: 延滞料金を計算")
        print("10: 終了")

        try:
            choice = int(input("操作を選択してください（1-10）: "))

            if choice == 1:
                book_id = input("図書IDを入力してください: ")
                title = input("タイトルを入力してください: ")
                author = input("著者名を入力してください: ")
                copies = int(input("冊数を入力してください: "))
                add_book(book_id, title, author, copies)

            elif choice == 2:
                list_books()

            elif choice == 3:
                book_id = input("検索する図書IDを入力してください: ")
                search_book(book_id)

            elif choice == 4:
                member_id = input("会員IDを入力してください: ")
                name = input("名前を入力してください: ")
                add_member(member_id, name)

            elif choice == 5:
                list_members()

            elif choice == 6:
                book_id = input("貸し出す図書IDを入力してください: ")
                member_id = input("会員IDを入力してください: ")
                borrow_book(book_id, member_id)

            elif choice == 7:
                list_borrowed_books()

            elif choice == 8:
                book_id = input("返却する図書IDを入力してください: ")
                member_id = input("会員IDを入力してください: ")
                return_book(book_id, member_id)

            elif choice == 9:
                calculate_fines()

            elif choice == 10:
                print("図書館管理システムを終了します。")
                break

            else:
                print("無効な選択です。1-10の数字を入力してください。")

        except ValueError as e:
            print(f"入力エラー: {e}")
        except Exception as e:
            print(f"予期しないエラーが発生しました: {e}")


# OpenAI APIキーの読み込み
load_dotenv()

# 画面の設定
st.set_page_config(
    page_title="図書館AIアプリ",
    page_icon="📚"
)

# 図書館データの初期化
for key in ["books", "members", "borrow_records"]:
    if key not in st.session_state:
        st.session_state[key] = []
    globals()[key] = st.session_state[key]


# AIから回答を取得する関数
def get_ai_response(user_text, expert_type):

    system_messages = {
        "図書館司書": (
            "あなたは図書館司書の専門家です。"
            "図書館の利用方法や本の貸出・返却について、"
            "初心者にもわかりやすく回答してください。"
        ),
        "読書アドバイザー": (
            "あなたは読書アドバイザーの専門家です。"
            "読者の興味や目的に合わせて、"
            "おすすめの本や読書方法を提案してください。"
        )
    }

    # 登録図書の情報を取得
    catalog = "\n".join(
        f"{book['title']} / 著者: {book['author']} / "
        f"在庫: {book['available_copies']}冊"
        for book in books
    ) or "登録図書なし"

    # プロンプトの作成
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_messages[expert_type]),
        (
            "human",
            "現在の登録図書:\n{catalog}\n\n"
            "ユーザーの質問:\n{question}\n\n"
            "登録されていない図書を、"
            "在庫ありと断定しないでください。"
        )
    ])

    # OpenAIとの連携
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7
    )

    chain = prompt | llm | StrOutputParser()

    # AIの回答を返す
    return chain.invoke({
        "catalog": catalog,
        "question": user_text
    })


# メイン画面
st.title("📚 図書館AIアプリ")

st.write(
    "図書の登録・貸出管理と、"
    "AI専門家への相談ができるWebアプリです。"
)

st.info(
    "「AIに相談」では専門家を選んで質問できます。"
    "「図書館管理」では本の登録や貸出・返却ができます。"
)

tab1, tab2 = st.tabs([
    "🤖 AIに相談",
    "📖 図書館管理"
])


# AI相談画面
with tab1:

    st.subheader("AI専門家に相談")

    expert = st.radio(
        "相談する専門家を選択してください",
        ["図書館司書", "読書アドバイザー"]
    )

    user_input = st.text_area(
        "相談内容を入力してください",
        placeholder="例：読書初心者におすすめの本は？"
    )

    if st.button("AIに質問する"):

        if not user_input.strip():
            st.warning("質問を入力してください。")

        elif not os.getenv("OPENAI_API_KEY"):
            st.error(
                "OpenAI APIキーが設定されていません。"
            )

        else:
            try:
                with st.spinner("AIが回答を作成しています..."):
                    answer = get_ai_response(
                        user_input,
                        expert
                    )

                st.subheader("AIからの回答")
                st.write(answer)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")


# 図書館管理画面
with tab2:

    st.subheader("図書館管理システム")

    st.caption(
        "登録データは一時保存です。"
        "サーバーを再起動すると消える場合があります。"
    )

    menu = [
        "図書を追加",
        "図書一覧を表示",
        "図書を検索",
        "会員を追加",
        "会員一覧を表示",
        "図書を貸し出す",
        "貸出中の図書一覧を表示",
        "図書を返却",
        "延滞料金を計算"
    ]

    choice = st.selectbox(
        "操作を選択してください",
        menu
    )

    with st.form("library_form"):

        func = None
        args = ()

        if choice == "図書を追加":
            book_id = st.text_input("図書ID")
            title = st.text_input("タイトル")
            author = st.text_input("著者名")
            copies = st.number_input(
                "冊数",
                min_value=1,
                step=1
            )
            func = add_book
            args = (book_id, title, author, copies)

        elif choice == "図書一覧を表示":
            func = list_books

        elif choice == "図書を検索":
            book_id = st.text_input("図書ID")
            func = search_book
            args = (book_id,)

        elif choice == "会員を追加":
            member_id = st.text_input("会員ID")
            name = st.text_input("名前")
            func = add_member
            args = (member_id, name)

        elif choice == "会員一覧を表示":
            func = list_members

        elif choice == "図書を貸し出す":
            book_id = st.text_input("図書ID")
            member_id = st.text_input("会員ID")
            func = borrow_book
            args = (book_id, member_id)

        elif choice == "貸出中の図書一覧を表示":
            func = list_borrowed_books

        elif choice == "図書を返却":
            book_id = st.text_input("図書ID")
            member_id = st.text_input("会員ID")
            func = return_book
            args = (book_id, member_id)

        elif choice == "延滞料金を計算":
            func = calculate_fines

        submitted = st.form_submit_button("実行")

    if submitted:

        if any(
            isinstance(value, str) and not value.strip()
            for value in args
        ):
            st.warning("必要な項目を入力してください。")

        else:
            output = io.StringIO()

            try:
                with redirect_stdout(output):
                    func(*args)

                st.text(output.getvalue())

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

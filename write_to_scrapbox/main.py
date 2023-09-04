import scrapbox_io
import iterative_commenter


def main(dry=False):
    pages = iterative_commenter.main()
    scrapbox_io.write_pages(pages)
    print("write ok")


if __name__ == "__main__":
    main()

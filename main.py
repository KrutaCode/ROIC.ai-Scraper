import pandas as pd
import Scraper.scraper

# Database management
import Database_Writer.database

# Excel sheet writing
import Excel_Writer.excel_writer

'-------------------------------------------------------'
'-------------------------------------------------------'
'-------------------------------------------------------'
def write_to_database(db: Database_Writer, df: pd.DataFrame, table_name: str):
    db.create_table_from_dataframe(df,table_type=table_name)

'-------------------------------------------------------'
def set_summary(s: Scraper, db: Database_Writer):
    exists = db.check_if_table_exists("summary")
    print(f"Exist: {exists}")
'-------------------------------------------------------'
'-------------------------------------------------------'
 






def main():
    ticker = "BBBY"

    scraper = Scraper.scraper.ROIC_Scraper(ticker)


    # Create excel sheet object
    excel = Excel_Writer.excel_writer.ExcelWriter(ticker)

    #
    summary_df = scraper.create_summary_page_df()
    if '' in summary_df.columns:
        # axis 0 = rows     axis 1 = columns
        summary_df.drop(summary_df.columns[-1], inplace=True, axis=1)
    income_statement_df = scraper.create_income_statement_df()
    if '' in income_statement_df.columns:
        income_statement_df.drop(income_statement_df.columns[-1], inplace=True, axis=1)
    balance_sheet_df = scraper.create_balance_sheet_df()
    if '' in balance_sheet_df.columns:
        balance_sheet_df.drop(balance_sheet_df.columns[-1], inplace=True, axis=1)
    cash_flow_df = scraper.create_cash_flow_df()
    if '' in cash_flow_df.columns:
        cash_flow_df.drop(cash_flow_df.columns[-1], inplace=True, axis=1)

    # Database inserts
    scraper.db.create_table_from_dataframe(summary_df, table_type="summary")
    scraper.db.create_table_from_dataframe(income_statement_df, table_type="income_statement")
    scraper.db.create_table_from_dataframe(balance_sheet_df, table_type="balance_sheet")
    scraper.db.create_table_from_dataframe(cash_flow_df, table_type="cash_flow")

    excel.write_to_file(summary_df, income_statement_df, balance_sheet_df, cash_flow_df)




main()
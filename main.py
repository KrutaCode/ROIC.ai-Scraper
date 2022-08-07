# For number storage and manipulation.
import pandas as pd

# Webscraper object to collect data.
import Scraper.scraper


# Excel sheet object to write data to an excel file. 
import Excel_Writer.excel_writer

def main():
    ticker = "AAPL"

    scraper = Scraper.scraper.ROIC_Scraper(ticker)


    # Create excel sheet object
    excel = Excel_Writer.excel_writer.ExcelWriter(ticker)

    # Create a dataframe from the data collected by the webscraper. 
    # Summary Page
    summary_df = scraper.create_summary_page_df()
    if '' in summary_df.columns:
        # axis 0 = rows     axis 1 = columns
        summary_df.drop(summary_df.columns[-1], inplace=True, axis=1)
    # Income Statement
    income_statement_df = scraper.create_income_statement_df()
    if '' in income_statement_df.columns:
        income_statement_df.drop(income_statement_df.columns[-1], inplace=True, axis=1)
    # Balance Sheet
    balance_sheet_df = scraper.create_balance_sheet_df()
    if '' in balance_sheet_df.columns:
        balance_sheet_df.drop(balance_sheet_df.columns[-1], inplace=True, axis=1)
    # Cash Flow Statement
    cash_flow_df = scraper.create_cash_flow_df()
    if '' in cash_flow_df.columns:
        cash_flow_df.drop(cash_flow_df.columns[-1], inplace=True, axis=1)

    # Database inserts
    scraper.db.create_table_from_dataframe(summary_df, table_type="summary")
    scraper.db.create_table_from_dataframe(income_statement_df, table_type="income_statement")
    scraper.db.create_table_from_dataframe(balance_sheet_df, table_type="balance_sheet")
    scraper.db.create_table_from_dataframe(cash_flow_df, table_type="cash_flow")
    
    # Send dataframes to excel writer where they will be written to the file. 
    excel.write_to_file(summary_df, income_statement_df, balance_sheet_df, cash_flow_df)




main()

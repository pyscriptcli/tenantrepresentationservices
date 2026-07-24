import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from openpyxl.utils import get_column_letter, range_boundaries
import re
import io
import requests
from copy import copy
import os
import hashlib
from openpyxl import load_workbook
import streamlit.components.v1 as components
import base64
from datetime import datetime
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import pyarrow as pa
import pyarrow.parquet as pq
import json
import traceback
import gc

#--- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="trs.sitesourcing.viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#--- HTML FRAMEWORK ---
HTML_FRAMEWORK = """
| SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
|SITE INFORMATION REPORT
| |
| ---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| General Information
|General Information
|General Information
|General Information
|General Information
|General Information
|General Information
||Location
|Location
|Location
|Location
|Location
|Location
|Location
| |
| ||||||||||||||| |
| Trade Area Name
||_TRADE_AREA_
|_TRADE_AREA_
|_TRADE_AREA_
|_TRADE_AREA_
|_TRADE_AREA_
||Site Name
|Site Name
|_SITE_NAME_
|_SITE_NAME_
|_SITE_NAME_
|_SITE_NAME_
|_SITE_NAME_
| |
| Site Name:
||_SITE_NAME_
|_SITE_NAME_
|_SITE_NAME_
|_SITE_NAME_
|_SITE_NAME_
||Unit #, Bldg/St # and St Name
|Unit #, Bldg/St # and St Name
|_UNIT_BLDG_ST_NAME_
|_UNIT_BLDG_ST_NAME_
|_UNIT_BLDG_ST_NAME_
|_UNIT_BLDG_ST_NAME_
|_UNIT_BLDG_ST_NAME_
| |
| Site Number:
||_SITE_NO_
|_SITE_NO_
|_SITE_NO_
|_SITE_NO_
|_SITE_NO_
||Barangay/District Name
|Barangay/District Name
|_BARANGAY_DISTRICT_NAME_
|_BARANGAY_DISTRICT_NAME_
|_BARANGAY_DISTRICT_NAME_
|_BARANGAY_DISTRICT_NAME_
|_BARANGAY_DISTRICT_NAME_
| |
| Date Started
||_TIMESTAMP_
|_TIMESTAMP_
|_TIMESTAMP_
|_TIMESTAMP_
|_TIMESTAMP_
||City/Municipality
|City/Municipality
|_CITY_MUNICIPALITY_
|_CITY_MUNICIPALITY_
|_CITY_MUNICIPALITY_
|_CITY_MUNICIPALITY_
|_CITY_MUNICIPALITY_
| |
| Date Report Submitted
|Date Report Submitted
|_DATE_OF_REPORT_
|_DATE_OF_REPORT_
|_DATE_OF_REPORT_
|_DATE_OF_REPORT_
|_DATE_OF_REPORT_
||Region
|Region
|_REGION_
|_REGION_
|_REGION_
|_REGION_
|_REGION_
| |
| ||||||||Postal Code
|Postal Code
|_POSTAL_CODE_
|_POSTAL_CODE_
|_POSTAL_CODE_
|_POSTAL_CODE_
|_POSTAL_CODE_
| |
| ||||||||||||||| |
| Terms
|Terms
|Terms
|Terms
|Terms
|Terms
|Terms
||Rates
|Rates
|Rates
|Rates
|Rates
|Rates
|Rates
| |
| ||||||||||||||| |
| Site Availability Date
||_SITE_AVAILABILITY_DATE_
|_SITE_AVAILABILITY_DATE_
|_SITE_AVAILABILITY_DATE_
|_SITE_AVAILABILITY_DATE_
|_SITE_AVAILABILITY_DATE_
||Monthly Rental Rate (Php)
|Monthly Rental Rate (Php)
|_MONTHLY_RENTAL_RATE_
|_MONTHLY_RENTAL_RATE_
|_MONTHLY_RENTAL_RATE_
|_MONTHLY_RENTAL_RATE_
|_MONTHLY_RENTAL_RATE_
| |
| COL Start Date
||_COL_START_DATE_
|_COL_START_DATE_
|_COL_START_DATE_
|_COL_START_DATE_
|_COL_START_DATE_
||Percentage Rent
|Percentage Rent
|_PERCENTAGE_RENT_
|_PERCENTAGE_RENT_
|_PERCENTAGE_RENT_
|_PERCENTAGE_RENT_
|_PERCENTAGE_RENT_
| |
| COL End Date
||_COL_END_DATE_
|_COL_END_DATE_
|_COL_END_DATE_
|_COL_END_DATE_
|_COL_END_DATE_
||Minimum Guaranteed Rent
|Minimum Guaranteed Rent
|_MINIMUM_GUARANTEED_RENT_
|_MINIMUM_GUARANTEED_RENT_
|_MINIMUM_GUARANTEED_RENT_
|_MINIMUM_GUARANTEED_RENT_
|_MINIMUM_GUARANTEED_RENT_
| |
| Lease Terms
||_LEASE_TERMS_
|_LEASE_TERMS_
|_LEASE_TERMS_
|_LEASE_TERMS_
|_LEASE_TERMS_
||Annual Escalation Rate (%)
|Annual Escalation Rate (%)
|_ESCALATION_
|_ESCALATION_
|_ESCALATION_
|_ESCALATION_
|_ESCALATION_
| |
| ||||||||Advance Rental (Php)
|Advance Rental (Php)
|_ADVANCE_RENTAL_
|_ADVANCE_RENTAL_
|_ADVANCE_RENTAL_
|_ADVANCE_RENTAL_
|_ADVANCE_RENTAL_
| |
| Technical Info
|Technical Info
|Technical Info
|Technical Info
|Technical Info
|Technical Info
|Technical Info
||Security Deposit Amount (Php)
|Security Deposit Amount (Php)
|_SECURITY_DEPOSIT_
|_SECURITY_DEPOSIT_
|_SECURITY_DEPOSIT_
|_SECURITY_DEPOSIT_
|_SECURITY_DEPOSIT_
| |
| ||||||||CUSA Dues
|CUSA Dues
|_CUSA_
|_CUSA_
|_CUSA_
|_CUSA_
|_CUSA_
| |
| Lot/Floor Area (in sqm)
|Lot/Floor Area (in sqm)
|_LOT_FLOOR_AREA_SQM_
|_LOT_FLOOR_AREA_SQM_
|_LOT_FLOOR_AREA_SQM_
|_LOT_FLOOR_AREA_SQM_
|_LOT_FLOOR_AREA_SQM_
||Estimated Revenue Per Mo.
|Estimated Revenue Per Mo.
|_ESTIMATED_REVENUE_PER_MO_
|_ESTIMATED_REVENUE_PER_MO_
|_ESTIMATED_REVENUE_PER_MO_
|_ESTIMATED_REVENUE_PER_MO_
|_ESTIMATED_REVENUE_PER_MO_
| |
| Frontage (in m)
||_FRONTAGE_
|_FRONTAGE_
|_FRONTAGE_
|_FRONTAGE_
|_FRONTAGE_
||||||||| |
| Depth (in m)
||_DEPTH_IN_M_
|_DEPTH_IN_M_
|_DEPTH_IN_M_
|_DEPTH_IN_M_
|_DEPTH_IN_M_
||Provisions
|Provisions
|Provisions
|Provisions
|Provisions
|Provisions
|Provisions
| |
| Floor to Slab Height (in m) - if Bldg
|Floor to Slab Height (in m) - if Bldg
|_FLOOR_TO_SLAB_HEIGHT_IN_M_IF_BLDG_
|_FLOOR_TO_SLAB_HEIGHT_IN_M_IF_BLDG_
|_FLOOR_TO_SLAB_HEIGHT_IN_M_IF_BLDG_
|_FLOOR_TO_SLAB_HEIGHT_IN_M_IF_BLDG_
|_FLOOR_TO_SLAB_HEIGHT_IN_M_IF_BLDG_
||||||||| |
| No. of Storeys (If Bldg Lessee)
|No. of Storeys (If Bldg Lessee)
|_NO_OF_STOREYS_
|_NO_OF_STOREYS_
|_NO_OF_STOREYS_
|_NO_OF_STOREYS_
|_NO_OF_STOREYS_
||Tenant is the Owner
|Tenant is the Owner
|_TENANT_IS_THE_OWNER_
|_TENANT_IS_THE_OWNER_
|_TENANT_IS_THE_OWNER_
|_TENANT_IS_THE_OWNER_
|_TENANT_IS_THE_OWNER_
| |
| Type of Structure (if Bldg Lessee)
|Type of Structure (if Bldg Lessee)
|_TYPE_OF_STRUCTURE_IF_BLDG_LESSEE_
|_TYPE_OF_STRUCTURE_IF_BLDG_LESSEE_
|_TYPE_OF_STRUCTURE_IF_BLDG_LESSEE_
|_TYPE_OF_STRUCTURE_IF_BLDG_LESSEE_
|_TYPE_OF_STRUCTURE_IF_BLDG_LESSEE_
||Lease Type
|Lease Type
|_LEASE_TYPE_
|_LEASE_TYPE_
|_LEASE_TYPE_
|_LEASE_TYPE_
|_LEASE_TYPE_
| |
| Soil Profile
||_SOIL_PROFILE_
|_SOIL_PROFILE_
|_SOIL_PROFILE_
|_SOIL_PROFILE_
|_SOIL_PROFILE_
||Principal COL
|Principal COL
|_PRINCIPAL_COL_
|_PRINCIPAL_COL_
|_PRINCIPAL_COL_
|_PRINCIPAL_COL_
|_PRINCIPAL_COL_
| |
| Supply Access:
||||||||Sub-Lease Provision
|Sub-Lease Provision
|_SUB_LEASE_PROVISION_
|_SUB_LEASE_PROVISION_
|_SUB_LEASE_PROVISION_
|_SUB_LEASE_PROVISION_
|_SUB_LEASE_PROVISION_
| |
| Power
||Aircon
||LPG Fire Pro
|LPG Fire Pro
|||Pre-Term/Partial Term
|Pre-Term/Partial Term
|_PRE_TERM_PARTIAL_TERM_
|_PRE_TERM_PARTIAL_TERM_
|_PRE_TERM_PARTIAL_TERM_
|_PRE_TERM_PARTIAL_TERM_
|_PRE_TERM_PARTIAL_TERM_
| |
| Water
||Exhaust
||Drainage TP
|Drainage TP
|||Tripartite Agreement
|Tripartite Agreement
|_TRIPARTITE_AGREEMENT_
|_TRIPARTITE_AGREEMENT_
|_TRIPARTITE_AGREEMENT_
|_TRIPARTITE_AGREEMENT_
|_TRIPARTITE_AGREEMENT_
| |
| ||||||||||||||| |
| Lessor and Tenant Details
|Lessor and Tenant Details
|Lessor and Tenant Details
|Lessor and Tenant Details
|Lessor and Tenant Details
|Lessor and Tenant Details
|Lessor and Tenant Details
||If with Sub-Lessor/ Sub-Lessee
|If with Sub-Lessor/ Sub-Lessee
|If with Sub-Lessor/ Sub-Lessee
|If with Sub-Lessor/ Sub-Lessee
|If with Sub-Lessor/ Sub-Lessee
|If with Sub-Lessor/ Sub-Lessee
|If with Sub-Lessor/ Sub-Lessee
| |
| ||||||||||||||| |
| Name of Lessor
||_LESSOR_
|_LESSOR_
|_LESSOR_
|_LESSOR_
|_LESSOR_
||Name of Sub-Lessor
|Name of Sub-Lessor
|_NAME_OF_SUBLESSOR_
|_NAME_OF_SUBLESSOR_
|_NAME_OF_SUBLESSOR_
|_NAME_OF_SUBLESSOR_
|_NAME_OF_SUBLESSOR_
| |
| Contact No.
||_LESSOR_CONTACT_NO_
|_LESSOR_CONTACT_NO_
|_LESSOR_CONTACT_NO_
|_LESSOR_CONTACT_NO_
|_LESSOR_CONTACT_NO_
||Contact No.
|Contact No.
|_SUBLESSOR_CONTACT_NO_
|_SUBLESSOR_CONTACT_NO_
|_SUBLESSOR_CONTACT_NO_
|_SUBLESSOR_CONTACT_NO_
|_SUBLESSOR_CONTACT_NO_
| |
| E-mail Address
||_LESSOR_EMAIL_ADDRESS_
|_LESSOR_EMAIL_ADDRESS_
|_LESSOR_EMAIL_ADDRESS_
|_LESSOR_EMAIL_ADDRESS_
|_LESSOR_EMAIL_ADDRESS_
||E-mail Address
|E-mail Address
|_SUBLESSOR_EMAIL_ADDRESS_
|_SUBLESSOR_EMAIL_ADDRESS_
|_SUBLESSOR_EMAIL_ADDRESS_
|_SUBLESSOR_EMAIL_ADDRESS_
|_SUBLESSOR_EMAIL_ADDRESS_
| |
| Type of Ownership
||_LESSOR_TYPE_OF_OWNERSHIP_
|_LESSOR_TYPE_OF_OWNERSHIP_
|_LESSOR_TYPE_OF_OWNERSHIP_
|_LESSOR_TYPE_OF_OWNERSHIP_
|_LESSOR_TYPE_OF_OWNERSHIP_
||Type of Ownership
|Type of Ownership
|_SUBLESSOR_TYPE_OF_OWNERSHIP_
|_SUBLESSOR_TYPE_OF_OWNERSHIP_
|_SUBLESSOR_TYPE_OF_OWNERSHIP_
|_SUBLESSOR_TYPE_OF_OWNERSHIP_
|_SUBLESSOR_TYPE_OF_OWNERSHIP_
| |
| Company Name
||_LESSOR_COMPANY_NAME_
|_LESSOR_COMPANY_NAME_
|_LESSOR_COMPANY_NAME_
|_LESSOR_COMPANY_NAME_
|_LESSOR_COMPANY_NAME_
||Company Name
|Company Name
|_SUBLESSOR_COMPANY_NAME_
|_SUBLESSOR_COMPANY_NAME_
|_SUBLESSOR_COMPANY_NAME_
|_SUBLESSOR_COMPANY_NAME_
|_SUBLESSOR_COMPANY_NAME_
| |
| Developer Account Name
|Developer Account Name
|_LESSOR_DEVELOPER_ACCOUNT_NAME_
|_LESSOR_DEVELOPER_ACCOUNT_NAME_
|_LESSOR_DEVELOPER_ACCOUNT_NAME_
|_LESSOR_DEVELOPER_ACCOUNT_NAME_
|_LESSOR_DEVELOPER_ACCOUNT_NAME_
||Developer Account Name
|Developer Account Name
|_SUBLESSOR_DEVELOPER_ACCOUNT_NAME_
|_SUBLESSOR_DEVELOPER_ACCOUNT_NAME_
|_SUBLESSOR_DEVELOPER_ACCOUNT_NAME_
|_SUBLESSOR_DEVELOPER_ACCOUNT_NAME_
|_SUBLESSOR_DEVELOPER_ACCOUNT_NAME_
| |
| Business Address
||_LESSOR_BUSINESS_ADDRESS_
|_LESSOR_BUSINESS_ADDRESS_
|_LESSOR_BUSINESS_ADDRESS_
|_LESSOR_BUSINESS_ADDRESS_
|_LESSOR_BUSINESS_ADDRESS_
||Business Address
|Business Address
|_SUBLESSOR_BUSINESS_ADDRESS_
|_SUBLESSOR_BUSINESS_ADDRESS_
|_SUBLESSOR_BUSINESS_ADDRESS_
|_SUBLESSOR_BUSINESS_ADDRESS_
|_SUBLESSOR_BUSINESS_ADDRESS_
| |
| Name of Authorized Representative
|Name of Authorized Representative
|_LESSOR_AUTHORIZED_REPRESENTATIVE_
|_LESSOR_AUTHORIZED_REPRESENTATIVE_
|_LESSOR_AUTHORIZED_REPRESENTATIVE_
|_LESSOR_AUTHORIZED_REPRESENTATIVE_
|_LESSOR_AUTHORIZED_REPRESENTATIVE_
||Name of Authorized Representative
|Name of Authorized Representative
|_SUBLESSOR_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_SUBLESSOR_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_SUBLESSOR_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_SUBLESSOR_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_SUBLESSOR_NAME_OF_AUTHORIZED_REPRESENTATIVE_
| |
| Residence Address of Authorized Representative
|Residence Address of Authorized Representative
|_LESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
|_LESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
|_LESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
|_LESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
|_LESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
||Residence Address of Authorized Representative
|Residence Address of Authorized Representative
|_SUBLESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
|_SUBLESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
|_SUBLESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
|_SUBLESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
|_SUBLESSOR_RESIDENCE_ADDRESS_OF_AUTHORIZED_REPRESENTATIVE_
| |
| Contact No.
||_LESSOR_AUTHORIZED_REP_CONTACT_NO_
|_LESSOR_AUTHORIZED_REP_CONTACT_NO_
|_LESSOR_AUTHORIZED_REP_CONTACT_NO_
|_LESSOR_AUTHORIZED_REP_CONTACT_NO_
|_LESSOR_AUTHORIZED_REP_CONTACT_NO_
||Contact No.
|Contact No.
|_SUBLESSOR_CONTACT_NO_
|_SUBLESSOR_CONTACT_NO_
|_SUBLESSOR_CONTACT_NO_
|_SUBLESSOR_CONTACT_NO_
|_SUBLESSOR_CONTACT_NO_
| |
| E-mail Address
||_LESSOR_AUTHORIZED_REP_EMAIL_
|_LESSOR_AUTHORIZED_REP_EMAIL_
|_LESSOR_AUTHORIZED_REP_EMAIL_
|_LESSOR_AUTHORIZED_REP_EMAIL_
|_LESSOR_AUTHORIZED_REP_EMAIL_
||E-mail Address
|E-mail Address
|_SUBLESSOR_EMAIL_ADDRESS_
|_SUBLESSOR_EMAIL_ADDRESS_
|_SUBLESSOR_EMAIL_ADDRESS_
|_SUBLESSOR_EMAIL_ADDRESS_
|_SUBLESSOR_EMAIL_ADDRESS_
| |
| ||||||||||||||||
| Name of Lessee
||_NAME_OF_LESSEE_
|_NAME_OF_LESSEE_
|_NAME_OF_LESSEE_
|_NAME_OF_LESSEE_
|_NAME_OF_LESSEE_
||Name of Sub-Lessee
|Name of Sub-Lessee
|_NAME_OF_SUB_LESSEE_
|_NAME_OF_SUB_LESSEE_
|_NAME_OF_SUB_LESSEE_
|_NAME_OF_SUB_LESSEE_
|_NAME_OF_SUB_LESSEE_
| |
| Position
||_LESSEE_POSITION_
|_LESSEE_POSITION_
|_LESSEE_POSITION_
|_LESSEE_POSITION_
|_LESSEE_POSITION_
||Position
|Position
|_SUB_LESSEE_POSITION_
|_SUB_LESSEE_POSITION_
|_SUB_LESSEE_POSITION_
|_SUB_LESSEE_POSITION_
|_SUB_LESSEE_POSITION_
| |
| Contact No.
||_LESSEE_CONTACT_NO_
|_LESSEE_CONTACT_NO_
|_LESSEE_CONTACT_NO_
|_LESSEE_CONTACT_NO_
|_LESSEE_CONTACT_NO_
||Contact No.
|Contact No.
|_SUB_LESSEE_CONTACT_NO_
|_SUB_LESSEE_CONTACT_NO_
|_SUB_LESSEE_CONTACT_NO_
|_SUB_LESSEE_CONTACT_NO_
|_SUB_LESSEE_CONTACT_NO_
| |
| E-mail Address
||_LESSEE_EMAIL_ADDRESS_
|_LESSEE_EMAIL_ADDRESS_
|_LESSEE_EMAIL_ADDRESS_
|_LESSEE_EMAIL_ADDRESS_
|_LESSEE_EMAIL_ADDRESS_
||E-mail Address
|E-mail Address
|_SUB_LESSEE_EMAIL_ADDRESS_
|_SUB_LESSEE_EMAIL_ADDRESS_
|_SUB_LESSEE_EMAIL_ADDRESS_
|_SUB_LESSEE_EMAIL_ADDRESS_
|_SUB_LESSEE_EMAIL_ADDRESS_
| |
| Name of Authorized Representative
|Name of Authorized Representative
|_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
||Name of Authorized Representative
|Name of Authorized Representative
|_SUB_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_SUB_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_SUB_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_SUB_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
|_SUB_LESSEE_NAME_OF_AUTHORIZED_REPRESENTATIVE_
| |
| Business Address
||_LESSEE_BUSINESS_ADDRESS_
|_LESSEE_BUSINESS_ADDRESS_
|_LESSEE_BUSINESS_ADDRESS_
|_LESSEE_BUSINESS_ADDRESS_
|_LESSEE_BUSINESS_ADDRESS_
||Business Address
|Business Address
|_SUB_LESSEE_BUSINESS_ADDRESS_
|_SUB_LESSEE_BUSINESS_ADDRESS_
|_SUB_LESSEE_BUSINESS_ADDRESS_
|_SUB_LESSEE_BUSINESS_ADDRESS_
|_SUB_LESSEE_BUSINESS_ADDRESS_
| |
| ||||||||||||||| |
| Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
|Regulatory
| |
| Setback Requirement
|_SETBACK_REQUIREMENT_
|_SETBACK_REQUIREMENT_
|_SETBACK_REQUIREMENT_
|Perm Traffic Re-Routing
|Perm Traffic Re-Routing
|_PERM_TRAFFIC_RE_ROUTING_
|_PERM_TRAFFIC_RE_ROUTING_
|_PERM_TRAFFIC_RE_ROUTING_
|Future Development
|Future Development
|_FUTURE_DEVELOPMENT_
|_FUTURE_DEVELOPMENT_
|_FUTURE_DEVELOPMENT_
|_FUTURE_DEVELOPMENT_
| |
| Road Widening
|_ROAD_WIDENING_
|_ROAD_WIDENING_
|_ROAD_WIDENING_
|Perm Road Closure
|Perm Road Closure
|_PERM_ROAD_CLOSURE_
|_PERM_ROAD_CLOSURE_
|_PERM_ROAD_CLOSURE_
|Zoning Clearance
|Zoning Clearance
|_ZONING_CLEARANCE_
|_ZONING_CLEARANCE_
|_ZONING_CLEARANCE_
|_ZONING_CLEARANCE_
| |
| Pedestrian Overpass
|_PEDESTRIAN_OVERPASS_
|_PEDESTRIAN_OVERPASS_
|_PEDESTRIAN_OVERPASS_
|Infrastructure Programs
|Infrastructure Programs
|_INFRASTRUCTURE_PROGRAMS_
|_INFRASTRUCTURE_PROGRAMS_
|_INFRASTRUCTURE_PROGRAMS_
|Gas Station
|Gas Station
|_GAS_STATION_
|_GAS_STATION_
|_GAS_STATION_
|_GAS_STATION_
| |
| ||||||||||||||| |
| Site Acquirability:
|Site Acquirability:
|Site Acquirability:
||||||||||||| |
| Confidence Level
|_CONFIDENCE_LEVEL_
|_CONFIDENCE_LEVEL_
|_CONFIDENCE_LEVEL_
|_CONFIDENCE_LEVEL_
|_CONFIDENCE_LEVEL_
|_CONFIDENCE_LEVEL_
||Site Availability
|Site Availability
|_SITE_AVAILABILITY_CLASS_
|_SITE_AVAILABILITY_CLASS_
|_SITE_AVAILABILITY_CLASS_
|_SITE_AVAILABILITY_CLASS_
|_SITE_AVAILABILITY_CLASS_
| |
| Other Remarks:
|_REMARKS_
|_REMARKS_
|_REMARKS_
|_REMARKS_
|_REMARKS_
|_REMARKS_
||Site Availability Remarks:
|Site Availability Remarks:
|_SITE_AVAILABILITY_REMARKS_
|_SITE_AVAILABILITY_REMARKS_
|_SITE_AVAILABILITY_REMARKS_
|_SITE_AVAILABILITY_REMARKS_
|_SITE_AVAILABILITY_REMARKS_
| |
"""

#--- FULL SCREEN LOADING OVERLAY ---
def get_loading_overlay_html(message="Loading data..."):
    return f"""
    <div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(15,31,56,0.85); z-index:9999; display:flex; align-items:center; justify-content:center; color:#fff; font-family:'Inter',sans-serif; font-size:1.2rem; letter-spacing:1px;">
        {message}
    </div>
    """

#--- GLOBAL STYLES ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --navy-dark: #0f1f38;
    --navy-light: #162845;
    --gold: #c8a658;
    --cream: #f8f7f5;
    --white: #ffffff;
}

/* Global & Body */
.stApp {
    background-color: var(--cream) !important;
    color: var(--navy-dark) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--navy-dark) !important;
    font-weight: 700 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--navy-dark) !important;
    color: var(--white) !important;
}
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stSelectbox label {
    color: var(--white) !important;
    font-family: 'Inter', sans-serif !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--gold) !important;
}

/* Buttons */
button[kind="primary"], div[data-testid="stForm"] button[kind="primary"] {
    background-color: var(--gold) !important;
    color: var(--navy-dark) !important;
    border: none !important;
    border-radius: 0px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    transition: all 0.3s ease !important;
}
button[kind="primary"]:hover {
    background-color: #b5954f !important;
    color: var(--navy-dark) !important;
}

button[kind="secondary"], div[data-testid="stForm"] button[kind="secondary"] {
    background-color: transparent !important;
    color: var(--navy-dark) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 0px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}
button[kind="secondary"]:hover {
    background-color: var(--gold) !important;
    color: var(--navy-dark) !important;
}

/* Cards & Containers */
div[data-testid="stMetric"], 
div[data-testid="stMetricContainer"],
div[data-testid="stDataFrameContainer"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--white) !important;
    border-radius: 0px !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(15, 31, 56, 0.05) !important;
    padding: 20px !important;
}

/* Inputs */
input, textarea, div[data-baseweb="select"] > div {
    border-radius: 0px !important;
    border: 1px solid var(--navy-dark) !important;
    background-color: var(--white) !important;
    font-family: 'Inter', sans-serif !important;
}
input:focus, textarea:focus {
    border: 1px solid var(--gold) !important;
    box-shadow: none !important;
}

/* Tabs */
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    border-radius: 0px !important;
    color: var(--navy-dark) !important;
    font-family: 'Inter', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-weight: 600 !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
    background-color: transparent !important;
}

/* Dividers */
hr {
    border-top: 1px solid var(--gold) !important;
    opacity: 0.5 !important;
}

/* Hide default streamlit footer and header for cleaner look */
footer, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

#--- SECURITY OBSERVERS ---
def deploy_workspace_security_protocols():
    injected_js = """
    <script>
        // Basic security observers placeholder
    </script>
    """
    components.html(injected_js, height=0, width=0)

deploy_workspace_security_protocols()

#--- LIGHT MODE LOCK ---
_config_dir = ".streamlit"
_config_file = os.path.join(_config_dir, "config.toml")
if not os.path.exists(_config_file):
    os.makedirs(_config_dir, exist_ok=True)
    with open(_config_file, "w", encoding="utf-8") as f:
        f.write('[theme]\nbase="light"\n')

#--- HARDCODED USERS (no JSON file) ---
HARDCODED_USERS = {
    "regis": {
        "password": "trs.jfc",
        "permissions": {"view_sir": True, "export_sir": True},
        "is_admin": False
    },
    "trs.aims": {
        "password": "trs.jfc",
        "permissions": {"view_sir": True, "export_sir": True},
        "is_admin": False
    },
    "jfc": {
        "password": "trs.prime",
        "permissions": {"view_sir": True, "export_sir": True},
        "is_admin": False
    },
    "admin": {
        "password": "@47t00M!!",
        "permissions": {"view_sir": True, "export_sir": True},
        "is_admin": True
    }
}

#--- SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = "member"
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'placeholders' not in st.session_state:
    st.session_state.placeholders = None
if 'template_bytes_raw' not in st.session_state:
    st.session_state.template_bytes_raw = None
if 'media_data_list' not in st.session_state:
    st.session_state.media_data_list = None
if 'cache_version' not in st.session_state:
    st.session_state.cache_version = 0
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []
if 'refresh_log' not in st.session_state:
     st.session_state.refresh_log = []
if 'cached_reports' not in st.session_state:
    st.session_state.cached_reports = {}
if 'cache_timestamp' not in st.session_state:
    st.session_state.cache_timestamp = None
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = None
if 'data_hash' not in st.session_state:
    st.session_state.data_hash =  None

#--- LOGIN FUNCTION ---
def authenticate(username, password):
    if username in HARDCODED_USERS and HARDCODED_USERS[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.role = "admin" if HARDCODED_USERS[username]["is_admin"] else "member"
        st.session_state.audit_log.append({"user": username, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        return True
    return False

#--- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=xlsx"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"

#--- DATA FORMATTING CONFIGURATION ---
FORMAT_CONFIG = {
    'TIMESTAMP': 'date',
    'DATE OF REPORT': 'date',
    'SITE AVAILABILITY DATE': 'date',
    'COL START DATE': 'date',
    'COL END DATE': 'date',
    'MONTHLY RENTAL RATE': 'number',
    'PERCENTAGE RENT': 'number',
    'MINIMUM GUARANTEED RENT': 'number',
    'ESCALATION': 'number',
    'ADVANCE RENTAL': 'number',
    'SECURITY DEPOSIT': 'number',
    'CUSA': 'number',
    'ESTIMATED REVENUE PER MO.': 'number',
    'LOT/FLOOR AREA SQM': 'number',
    'FRONTAGE': 'number',
    'DEPTH (IN M)': 'number',
}

def format_value(value, format_type='text'):
    if pd.isna(value) or value is None:
        return ""
    
    if format_type == 'date':
        if isinstance(value, datetime):
            return value.strftime('%B %d, %Y')
        if isinstance(value, str):
            try:
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        date_obj = datetime.strptime(value.strip(), fmt)
                        return date_obj.strftime('%B %d, %Y')
                    except ValueError:
                         continue
            except:
                pass
            return value
        if isinstance(value, (int, float)):
            try:
                from datetime import timedelta
                excel_epoch = datetime(1899, 12, 30)
                date_obj = excel_epoch + timedelta(days=float(value))
                return date_obj.strftime('%B %d, %Y')
            except:
                pass
        return str(value)
    
    elif format_type == 'number':
        try:
            num = float(str(value).replace(',', ''))
            if num.is_integer():
                return f"{int(num):,}"
            else:
                return f"{num:,.2f}"
        except:
            return str(value)
    
    elif format_type == 'currency':
        try:
            num = float(str(value).replace(',', '').replace('₱', ''))
            if num.is_integer():
                return f"₱{int(num):,}"
            else:
                return f"₱{num:,.2f}"
        except:
            return str(value)
    
    elif format_type == 'percent':
        try:
            num = float(str(value).replace('%', ''))
            return f"{num}%"
        except:
            return str(value)
    
    else:
        return str(value)

def extract_photo_url_from_cell(cell):
    if cell is None:
        return ""
    raw_val = cell.value if hasattr(cell, 'value') else cell
    if raw_val is None:
        return ""
    val_str = str(raw_val).strip()
    image_formula_match = re.search(r'IMAGE\s*\(\s*["\'](https?://[^"\']+)["\']', val_str, re.IGNORECASE)
    if image_formula_match:
        return image_formula_match.group(1)
    url_match = re.search(r'(https?://[^\s"\']+)', val_str)
    if url_match:
        return url_match.group(1)
    return val_str

def get_photo_display_value(cell):
    if cell is None or cell.value is None:
        return ""
    return extract_photo_url_from_cell(cell)

def download_file(url):
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        return None
    except Exception:
        return None

def clean_and_extract_url(cell_value):
    if cell_value is None:
        return ""
    val_str = str(cell_value).strip()
    formula_match = re.search(r'IMAGE\s*\(\s*["\'](https://[^"\']+)["\']', val_str, re.IGNORECASE)
    if formula_match:
        return formula_match.group(1)
    url_match = re.search(r'(https://[^\s"\']+)', val_str)
    if url_match:
        return url_match.group(1)
    return val_str

def extract_google_drive_id(clean_url):
    if not clean_url:
        return None
    match = re.search(r'(?:id=|/d/|/uc?.*?id=)([a-zA-Z0-9_-]{25,})', clean_url)
    return match.group(1) if match else None

def get_placeholders_optimized(template_bytes):
    try:
        wb = load_workbook(io.BytesIO(template_bytes), data_only=False)
        sheet = wb.active
        placeholders = set()
        for row in sheet.iter_rows(values_only=True):
            for val in row:
                 if isinstance(val, str):
                    matches = re.findall(r"{{(.*?)}}", val)
                    for match in matches:
                        name = match.split(":")[0].strip() if ":" in match else match.strip()
                        placeholders.add(name)
        wb.close()
        return sorted(list(placeholders))
    except Exception as e:
        st.error(f"Error extracting placeholders: {e}")
        return []

def sanitize_tab_name(name, existing_names):
    clean_name = re.sub(r'[/*?\[\]:]', '', str(name))[:31]
    if not clean_name: clean_name = "Sheet"
    if clean_name not in existing_names:
        existing_names.add(clean_name)
        return clean_name
    counter = 1
    while True:
        new_name = f"{clean_name[:27]} ({counter})"
        if new_name not in existing_names:
            existing_names.add(new_name)
            return new_name
        counter += 1

def parse_site_number(site_display_str):
    if not site_display_str:
        return float('inf')
    match = re.match(r"^(\d+(?:\.\d+)?)", str(site_display_str).strip())
    return float(match.group(1)) if match else float('inf')

def load_main_data_optimized(source_bytes):
    try:
        wb = load_workbook(io.BytesIO(source_bytes), data_only=True)
        ws = wb.active
        
        header_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip().upper() if h else "" for h in header_row]
        
        parsed_data_list = []
        for row in ws.iter_rows(min_row=2):
            row_dict = {}
            has_val = False
            
            for idx, cell in enumerate(row):
                if idx < len(headers) and headers[idx]:
                    raw_val = cell.value
                    
                    if raw_val is not None:
                        header_key = headers[idx]
                        format_type = FORMAT_CONFIG.get(header_key, 'text')
                        formatted_val = format_value(raw_val, format_type)
                    else:
                         formatted_val = ""
                    
                    cleaned_val = clean_and_extract_url(formatted_val)
                    row_dict[headers[idx]] = cleaned_val
                    
                    if cleaned_val != "" and cleaned_val is not None:
                        has_val = True
            
            if has_val:
                parsed_data_list.append(row_dict)
        
        wb.close()
        df = pd.DataFrame(parsed_data_list)
        df = df.loc[:, ~df.columns.str.contains('^$')]
        
        def create_site_display(row):
            site_no = row.get('SITE NO', '')
            site_name = row.get('SITE NAME', '')
            if pd.notna(site_no) and str(site_no).strip() != '':
                try:
                     f_val = float(str(site_no).strip())
                    if f_val.is_integer():
                        return f"{int(f_val)} - {site_name}"
                    else:
                        return f"{f_val} - {site_name}"
                except ValueError:
                    return f"{site_no} - {site_name}"
            return str(site_name)
            
        df["SITE_DISPLAY"] = df.apply(create_site_display, axis=1)
        return df
    except Exception as e:
        st.error(f"Error loading main data: {e}")
        return None

def load_media_data_optimized(source_bytes):
    try:
        wb = load_workbook(io.BytesIO(source_bytes), data_only=False)
        media_data_list = []
        media_ws = None
        
        for sheet_name in wb.sheetnames:
            if "PHOTO" in sheet_name.upper() or "DOC" in sheet_name.upper() or "MEDIA" in sheet_name.upper():
                media_ws = wb[sheet_name]
                break
        if not media_ws:
            media_ws = wb.active
        
        for row in media_ws.iter_rows():
            vals = []
            for cell in row:
                if cell is None:
                    vals.append("")
                else:
                    photo_url = extract_photo_url_from_cell(cell)
                    vals.append(photo_url)
            
            t_area = str(vals[13] if len(vals) > 13 and vals[13] is not None else "").strip()
            s_name = str(vals[15] if len(vals) > 15 and vals[15] is not None else "").strip()
             
            if t_area and s_name and t_area.upper() != "TRADE AREA":
                media_data_list.append({
                    'TRADE AREA': t_area,
                    'SITE NAME': s_name,
                    '__DIRECT_TCT': vals[2] if len(vals) > 2 else "",
                    '__DIRECT_LOT_PLAN': vals[3] if len(vals) > 3 else "",
                    '__DIRECT_BLDG_PLAN': vals[4] if len(vals) > 4 else "",
                    '__DIRECT_TAX_MAP': vals[5] if len(vals) > 5 else "",
                    '__DIRECT_PHOTO_1': vals[7] if len(vals) > 7 else "",
                    '__DIRECT_PHOTO_2': vals[8] if len(vals) > 8 else "",
                    '__DIRECT_PHOTO_3': vals[9] if len(vals) > 9 else "",
                    '__DIRECT_PHOTO_4': vals[10] if len(vals) > 10 else "",
                    '__DIRECT_PHOTO_5': vals[11] if len(vals) > 11 else "",
                })
        wb.close()
        return media_data_list
    except Exception as e:
        st.error(f"Error loading media data: {e}")
        return []

def download_and_process_all_data():
    start_time = time.time()
    
    with st.spinner("Loading data..."):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_source = executor.submit(download_file, SOURCE_URL)
            future_template = executor.submit(download_file, TEMPLATE_URL)
            source_bytes = future_source.result()
            template_bytes = future_template.result()
        
        if source_bytes is None or template_bytes is None: 
            return None, None, None, [], None
        
        source_data = source_bytes.getvalue()
        template_data = template_bytes.getvalue()
    
    with st.spinner("Loading media..."):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_main = executor.submit(load_main_data_optimized, source_data)
            future_media = executor.submit(load_media_data_optimized, source_data)
            df = future_main.result()
            media_data_list = future_media.result()
        
        if df is None:
            return None, None, None, [], None
        
        placeholders = get_placeholders_optimized(template_data)
    
    with st.spinner("Loading site information report..."):
        cached_reports = {}
        trade_areas = df["TRADE AREA"].dropna().unique()
        
        progress_bar = st.progress(0)
        for idx, trade_area in enumerate(trade_areas):
            report_bytes = generate_single_trade_area_report(
                trade_area, df, template_data, placeholders
            )
            cached_reports[trade_area] = report_bytes
            progress_bar.progress((idx + 1) / len(trade_areas))
        
        progress_bar.empty()
    
    elapsed = time.time() - start_time
    print(f"All data cached in {elapsed:.2f} seconds")
    
    return df, placeholders, template_data, media_data_list, cached_reports, datetime.now()

def generate_single_trade_area_report(trade_area, df, template_bytes_raw, placeholders):
    placeholders_sorted = sorted(placeholders, key=len, reverse=True)
    
    ta_data = df[df["TRADE AREA"] == trade_area]
    wb = load_workbook(io.BytesIO(template_bytes_raw))
    original_sheets = wb.sheetnames
    base_sheet = wb.active
    base_sheet.title = "TEMPLATE_TO_DELETE"
    existing_tabs = set()
    
    for _, r_row in ta_data.iterrows():
        s_name = r_row.get("SITE NAME", "Unknown") 
        safe_tab_name = sanitize_tab_name(s_name, existing_tabs)
        new_sheet = wb.copy_worksheet(base_sheet)
        new_sheet.title = safe_tab_name
        
        for row_cells in new_sheet.iter_rows():
            for cell in row_cells:
                if isinstance(cell.value, str) and "{{" in cell.value:
                    new_val = cell.value
                    for ph in placeholders_sorted:
                        target_regex = r"\{\{\s*" + re.escape(ph) + r"(\s*:.*?)?\}\}"
                        if re.search(target_regex, new_val):
                            raw_data_val = r_row.get(ph.upper(), "")
                            if pd.isna(raw_data_val) or raw_data_val is None:
                                raw_data_val = ""
                            val_str = str(raw_data_val)
                            new_val = re.sub(target_regex, val_str, new_val)
                    new_val = re.sub(r"\{\{.*?\}\}", "", new_val)
                    cell.value = new_val.strip() if new_val else ""
        
        for row in new_sheet.iter_rows():
            max_len = max([len(str(cell.value or '')) for cell in row])
            if max_len > 45:
                new_sheet.row_dimensions[row[0].row].height = None
    
    if "TEMPLATE_TO_DELETE" in wb.sheetnames:
        wb.remove(wb["TEMPLATE_TO_DELETE"])
    
    for name in original_sheets:
        if name in wb.sheetnames and name != "TEMPLATE_TO_DELETE":
            wb.remove(wb[name])
    
    wb_buffer = io.BytesIO()
    wb.save(wb_buffer)
    wb_buffer.seek(0)
    return wb_buffer.getvalue()

@st.cache_data(ttl=None, show_spinner=False)
def get_cached_data(cache_version):
    return download_and_process_all_data()

#--- MAIN APP ---
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<h1 style='text-align: center; font-family: Playfair Display, serif;'>TRS Site Information Report</h1>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter username", key="login_username")
        password = st.text_input("Password", placeholder="Enter password", type="password", key="login_password")
        if st.button("Login", use_container_width=True):
            if username and password:
                if authenticate(username, password):
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please enter both username and password.")
    st.stop()

if not st.session_state.data_loaded:
    loading_placeholder = st.empty()
    loading_placeholder.markdown(
        get_loading_overlay_html(message="Loading cached data..."), 
        unsafe_allow_html=True
    )

    result = get_cached_data(st.session_state.cache_version)
    
    if result and result[0] is not None:
        df, placeholders, template_bytes_raw, media_data_list, cached_reports, data_timestamp = result
        st.session_state.df = df
        st.session_state.placeholders = placeholders
        st.session_state.template_bytes_raw = template_bytes_raw
        st.session_state.media_data_list = media_data_list
        st.session_state.cached_reports = cached_reports
        st.session_state.cache_timestamp = data_timestamp
        st.session_state.last_refresh_time = datetime.now()
        
        df_hash = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()
        st.session_state.data_hash = df_hash
        
        st.session_state.data_loaded = True
        loading_placeholder.empty()
        st.rerun()
    else:
        loading_placeholder.empty()
        st.error("Failed to load data assets. Please verify link paths.")
        st.stop()

df = st.session_state.df
placeholders = st.session_state.placeholders
template_bytes_raw = st.session_state.template_bytes_raw
media_data_list = st.session_state.media_data_list
cached_reports = st.session_state.cached_reports

deploy_workspace_security_protocols()

if st.session_state.role == "admin":
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Admin Panel", "Viewer"], index=0)
else:
    page = "Viewer"

if st.session_state.role == "admin" and page == "Admin Panel":
    st.title("Admin Control Panel")
    
    st.subheader("Data Management")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        if st.session_state.cache_timestamp:
            cache_age = (datetime.now() - st.session_state.cache_timestamp).total_seconds()
            if cache_age < 60:
                age_str = f"{int(cache_age)} seconds"
            elif cache_age < 3600:
                age_str = f"{int(cache_age/60)} minutes"
            else:
                age_str = f"{int(cache_age/3600)} hours"
            st.metric("Cache Age", age_str)
        else:
            st.metric("Cache Age", "Not set")
    
    with col_info2:
        if st.session_state.df is not None:
            st.metric("Trade Areas", len(st.session_state.df["TRADE AREA"].dropna().unique()))
        else:
            st.metric("Trade Areas", "0")
    
    with col_info3:
        if st.session_state.cached_reports:
            st.metric("Cached Reports", len(st.session_state.cached_reports))
        else:
            st.metric("Cached Reports", "0")
    
    st.divider()
    
    col_refresh, col_status, col_clear = st.columns([1, 2, 1])
     
    with col_refresh:
        if st.button("Refresh All Data", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.session_state.cache_version += 1
            st.session_state.data_loaded = False
            st.session_state.cached_reports = {}
            st.session_state.refresh_log.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": st.session_state.username,
                "action": "Full data refresh"
            })
            st.success("Refresh initiated! Page will reload with fresh data...")
            time.sleep(1.5)
            st.rerun()
    
    with col_clear:
        if st.button("Clear Local Cache", use_container_width=True):
            st.cache_data.clear()
            st.session_state.cache_version += 1
            st.session_state.data_loaded = False
            st.session_state.cached_reports = {}
            st.success("Cache cleared! Reloading...")
            time.sleep(1)
            st.rerun()
    
    with col_status:
        if st.session_state.refresh_log:
            last_refresh = st.session_state.refresh_log[-1]
            if isinstance(last_refresh, dict):
                st.write(f"Last refresh: {last_refresh.get('timestamp', 'Unknown')}")
                st.write(f"By: {last_refresh.get('user', 'Unknown')}")
            else:
                st.write(f"Last refresh: {last_refresh}")
            
            if st.session_state.cache_timestamp:
                total_refreshes = len([log for log in st.session_state.refresh_log if isinstance(log, dict) and log.get('action') == 'Full data refresh'])
                st.write(f"Total refreshes: {total_refreshes}")
        else:
            st.write("No refresh performed yet")
    
    st.divider()
    
    with st.expander("Cache Statistics", expanded=False):
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.write("**Data Sizes:**")
            if st.session_state.df is not None:
                st.write(f"DataFrame: {st.session_state.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            if st.session_state.media_data_list:
                st.write(f"Media entries: {len(st.session_state.media_data_list)}")
        with col_stats2:
            st.write("**Cached Reports:**")
            if st.session_state.cached_reports:
                total_size = sum(len(report) for report in st.session_state.cached_reports.values())
                st.write(f"Total reports: {len(st.session_state.cached_reports)}")
                st.write(f"Total size: {total_size / 1024 / 1024:.2f} MB")
        with col_stats3:
            st.write("**Performance:**")
            if st.session_state.cache_timestamp:
                age = (datetime.now() - st.session_state.cache_timestamp).total_seconds()
                st.write(f"Cache age: {age:.0f} seconds")
    
    st.divider()
    
    st.subheader("Audit Log")
    audits = st.session_state.audit_log
    if audits:
        df_audit = pd.DataFrame(audits)
        summary = df_audit.groupby("user")["timestamp"].agg(["count", lambda x: list(x)]).reset_

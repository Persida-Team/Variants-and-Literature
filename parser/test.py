# import pmc_txt_parser as ptp
# import pmc_xml_parser as pxp
import combined_parsing
import os 
if __name__ == "__main__":
    data_path = "data"
    pmc_id_prefix = "PMC000xxxxxx"
    txt_path = os.path.join(data_path,"txt",pmc_id_prefix)
    print(os.listdir(txt_path))
    # combined_parsing.combine_xml_and_txt(_,_)
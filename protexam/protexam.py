#!/usr/bin/python
#protexam.py
'''
This is the primary file for ProtExAM.
It is intended to call all submethods as modules.

ProtExAM is a system for extracting a set of protein mentions and
contexts from biomedical literature, such that the mentions correspond
to a given topic (e.g., the heart, lung cancer), are as comprehensive
as the literature will allow, and are context-sentitive. The last of
these properties allows for protein mentions to be filtered by type,
e.g., those observed to be expressed vs. negative mentions.

'''
__author__= "Harry Caufield"
__email__ = "jcaufield@mednet.ucla.edu"

import sys, argparse

import protexam_helpers as phlp
import protexam_query as pqry
import protexam_process as ppro
import protexam_output as pout
import protexam_settings as pset

## Constants and Options
parser = argparse.ArgumentParser()
query_group = parser.add_mutually_exclusive_group()
prot_group = parser.add_mutually_exclusive_group()
single_parse_group = parser.add_mutually_exclusive_group()
query_group.add_argument("--query", help="Search for documents matching a query, in quotes."
                                     " This will be passed to PubMed so please use"
                                     " PubMed search options, including MeSH terms.", 
					action="append")
query_group.add_argument("--query_file", help="Search for documents matching a query," 
                                         " starting with the name of a text file"
                                         " containing one search term per line."
                                         " By default, this assumes an OR"
                                         " relationship between all terms.",
					action="append")
prot_group.add_argument("--get_protein_entries",
                    help = "Retrieve full UniProtKB entries for a list of"
                           " UniProt accession codes, provided in a specified"
                           " filename with one code per line."
                           " Output is written to a file in its own folder,"
                           " bypassing all other steps."
 )
prot_group.add_argument("--get_protein_aliases", 
                    help = "Retrieve UniProtKB entries for a list of"
                           " UniProt accession codes, provided in a specified"
                           " filename with one code per line."
                           " Output is written to a file in its own folder,"
                           " bypassing all other steps and limited to"
                           " alternate protein names and identifiers."
 )
single_parse_group.add_argument("--up_xml_to_aliases", 
                    help = "Parse a single file of UniProtKB entry XML"
                           " to aliases. Useful if XML download succeeds"
                           " but parsing fails, or if the entry file"
                           " was obtained elsewhere and you only need"
                           " aliases."
 )
single_parse_group.add_argument("--extract_full_text_json", 
                    help = "If entries for full texts have been" 
							" downloaded from PubMed Central and now" 
							" reside in query folders, this option" 
							" will produce a JSON file containing" 
							" available document full-texts for each"
							" PubMed ID for each query."
							" The full text entries may then be used to"
							" enrich structured PubMed entries with" 
							" text beyond abstracts.",
							action="store_true"
 )
single_parse_group.add_argument("--combine_aliases_by_uniref", 
                    help = "Given an alias filename and a UniRef" 
							" mapping file filename (i.e., tab-delimited"
							" with a header, with UPIDs in the first" 
							" column and cluster IDs in the second" 
							" column), combine sets of aliases on the"
							" basis of UniRef membership. Writes to the"
							" current directory."
							" Provide alias filename first and uniref"
							" file second.",
							nargs=2,
 )
parser.add_argument("--auto", help="Run in automatic mode, accepting all options"
                                   " with a Yes.", 
					action="store_true")
     
parser.add_argument("--convert_pmc_xml", help="After downloading PubMed"
                                   " Central XML documents, transform"
                                   " to standard PubMed XML style."
                                   " Note this does not retain full"
                                   " text content in the new file.", 
					action="store_true")


args = parser.parse_args()

## Classes

## Functions

## Main
def main():
 
 print("** ProtExAM **")
 
 #A quick version check
 if sys.version_info[0] < 3:
		sys.exit("Not compatible with Python2 -- sorry!\n"
					"Exiting...")
 
 have_query = False
 have_prot_query = False
 
 #Protein queries should also be loaded from a delimited file,
 #ideally with the pandas read_csv function.
 #Just assume the accessions are in the first column.
 
 if args.get_protein_entries:
  have_prot_query = True
  query_list = []
  with open(args.get_protein_entries) as query_file:
			for query_item in query_file:
				query_list.append(query_item.rstrip())
  pqry.download_uniprot_entries(query_list, "full")
  sys.exit("Exiting...")
  
 if args.get_protein_aliases:
  have_prot_query = True
  query_list = []
  with open(args.get_protein_aliases) as query_file:
			for query_item in query_file:
				query_list.append(query_item.rstrip())
  pqry.download_uniprot_entries(query_list, "alias")
  sys.exit("Exiting...")
  
 if args.up_xml_to_aliases:
  query_list = []
  pqry.download_uniprot_entries(query_list, "alias_only", 
                                args.up_xml_to_aliases)
  sys.exit("Exiting...")

 if args.extract_full_text_json:
  ppro.extract_full_text_json()
  sys.exit("Exiting...")

 if args.combine_aliases_by_uniref:
  ppro.combine_aliases_by_uniref(args.combine_aliases_by_uniref)
  sys.exit("Exiting...") 
 
 if args.query:
  have_query = True
  query = (args.query)[0]
  pmid_list, query_dir_path, webenv = pqry.run_pubmed_query(query)
  log_file_path = phlp.write_log(query, query_dir_path)
  
 if args.query_file:
  have_query = True
  query_list = []
  with open(args.query_file) as query_file:
			for query_item in query_file:
				query_list.append(query_item.rstrip())
  pmid_list, query_dir_path, webenv = pqry.run_pubmed_query(query_list)
  log_file_path = phlp.write_log("\t".join(query_list), query_dir_path)
  
 if not have_query:
  sys.exit("No query provided. Please use the --query or --query_file "
           "options.\n"
  "Exiting...")
  
 if args.convert_pmc_xml:
  convert_pmc_xml = True
 else:
  convert_pmc_xml = False
 
 print("Saving records and logs to %s" % (query_dir_path))
 print("See %s for query details." % (log_file_path))
 
 #Prompt to continue - the function here is just an input parser
 question = "Continue with document download? (Y/N) "
 if not args.auto:
  response = phlp.get_input(question, "truefalse")
  if not response:
   sys.exit("OK, exiting...")
 else:
  print("%s Y" % (question))
 
 recs = pqry.download_pubmed_entries(pmid_list, query_dir_path, webenv)
 pqry.download_pmc_entries(recs, query_dir_path, webenv, convert_pmc_xml)
 
 print("Document download complete.")
 
 #Prompt to continue again
 question = "Continue with annotation download? (Y/N) "
 if not args.auto:
  response = phlp.get_input(question, "truefalse")
  if not response:
   sys.exit("OK, exiting...")
 else:
  print("%s Y" % (question))
 
 pqry.download_ptc_gene_annotations(pmid_list, query_dir_path)

 print("Annotation download complete.")
 
if __name__ == "__main__":
	sys.exit(main())


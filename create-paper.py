from src import *
import argparse
import json
import cairo

def get_free_markers(papers, count=1):
	free_markers = list(range(0, 250))
	
	for paper in papers:
		for marker in paper["markers"]:
			free_markers.remove(marker)
	
	return free_markers[:count]

def get_next_paper_id(papers):
	min_id = 0
	
	for paper in papers:
		if paper["id"] > min_id:
			min_id = paper["id"]
	
	return min_id+1

def create_video_paper(papers, args):
	paper_id = get_next_paper_id(papers)
	markers = get_free_markers(papers, count=4)
	
	data = {
		"id": paper_id,
		"type": "video",
		"markers": markers,
		"video_size": [480, 270],
		"video_file": args.file,
	}
	
	title = "Video(file={}) #{}".format(args.file, paper_id)
	
	return markers, data, title

def create_portal_in_paper(papers, args):
	paper_id = get_next_paper_id(papers)
	markers = get_free_markers(papers, count=4)
	
	data = {
		"id": paper_id,
		"type": "portal-in",
		"markers": markers,
	}
	
	title = "PortalIn #{}".format(paper_id)
	
	return markers, data, title

def create_portal_out_paper(papers, args):
	paper_id = get_next_paper_id(papers)
	markers = get_free_markers(papers, count=4)
	
	data = {
		"id": paper_id,
		"type": "portal-out",
		"markers": markers,
		"portal_in": args.portal_in,
	}
	
	title = "PortalOut(portal_in={}) #{}".format(args.portal_in, paper_id)
	
	return markers, data, title

def create_paper_from_args(papers, args):
	if args.type == "video":
		return create_video_paper(papers, args)
	elif args.type == "portal-in":
		return create_portal_in_paper(papers, args)
	elif args.type == "portal-out":
		return create_portal_out_paper(papers, args)

def main():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(dest="type")
	
	video_parser = subparsers.add_parser("video")
	video_parser.add_argument("--file", required=True)
	
	video_parser = subparsers.add_parser("portal-in")
	
	video_parser = subparsers.add_parser("portal-out")
	video_parser.add_argument("--portal-in")
	
	args = parser.parse_args()
	
	papers = []
	if os.path.exists("papers.json"):
		with open("papers.json", "r") as file:
			papers = json.load(file)
	
	markers, data, title = create_paper_from_args(papers, args)
	
	papers.append(data)
		
	with open("papers.json", "w") as file:
		json.dump(papers, file, indent=2)
			
	with cairo.PDFSurface("paper.pdf", DIN_A4_WIDTH_POINTS, DIN_A4_HEIGHT_POINTS) as surface:
		ctx = cairo.Context(surface)
		marker_imgs = get_marker_images(*markers)
		draw_rect_portrait_a4(ctx, marker_imgs, title=title)
	
	print("created", title)
	print("print paper.pdf")

if __name__ == "__main__":
	main()

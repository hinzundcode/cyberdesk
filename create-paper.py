import argparse
import os
import json
import cairo
from cyberdesk.vision import get_marker_images
from cyberdesk.paperspace import draw_rect_portrait_a4, draw_rect_landscape_a5, draw_single_marker, DIN_A4_WIDTH_POINTS, DIN_A4_HEIGHT_POINTS

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

def create_video_paper(papers, args, ctx):
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
	
	marker_imgs = get_marker_images(*markers)
	draw_rect_portrait_a4(ctx, marker_imgs, title=title)
	
	return markers, data, title

def create_portal_in_paper(papers, args, ctx):
	paper_id = get_next_paper_id(papers)
	markers = get_free_markers(papers, count=4)
	
	data = {
		"id": paper_id,
		"type": "portal-in",
		"markers": markers,
	}
	
	title = "PortalIn #{}".format(paper_id)
	
	marker_imgs = get_marker_images(*markers)
	draw_rect_portrait_a4(ctx, marker_imgs, title=title)
	
	return markers, data, title

def create_portal_out_paper(papers, args, ctx):
	paper_id = get_next_paper_id(papers)
	markers = get_free_markers(papers, count=4)
	
	data = {
		"id": paper_id,
		"type": "portal-out",
		"markers": markers,
		"portal_in": args.portal_in,
	}
	
	title = "PortalOut(portal_in={}) #{}".format(args.portal_in, paper_id)
	
	marker_imgs = get_marker_images(*markers)
	draw_rect_portrait_a4(ctx, marker_imgs, title=title)
	
	return markers, data, title

def create_gamepad_paper(papers, args, ctx):
	paper_id = get_next_paper_id(papers)
	markers = get_free_markers(papers, count=4)
	
	data = {
		"id": paper_id,
		"type": "gamepad",
		"markers": markers,
		"gamepad_id": args.gamepad_id,
	}
	
	title = "Gamepad(id={}) #{}".format(args.gamepad_id, paper_id)
	
	marker_imgs = get_marker_images(*markers)
	draw_rect_landscape_a5(ctx, marker_imgs, title=title)
	
	return markers, data, title

def create_python_paper(papers, args, ctx):
	paper_id = get_next_paper_id(papers)
	markers = get_free_markers(papers, count=4)
	
	data = {
		"id": paper_id,
		"type": "python",
		"markers": markers,
		"filename": args.filename,
	}
	
	title = "Python(filename={}) #{}".format(args.filename, paper_id)
	
	marker_imgs = get_marker_images(*markers)
	draw_rect_landscape_a5(ctx, marker_imgs, title=title)
	
	return markers, data, title

def create_shortcut_button_paper(papers, args, ctx):
	paper_id = get_next_paper_id(papers)
	markers = get_free_markers(papers, count=1)
	
	data = {
		"id": paper_id,
		"type": "shortcut-button",
		"markers": markers,
		"mqtt_topic": args.mqtt_topic,
		"mqtt_host": args.mqtt_host,
	}
	
	title = "ShortcutButton(mqtt_topic={}, mqtt_host={}) #{}".format(args.mqtt_topic, args.mqtt_host, paper_id)
	
	marker_imgs = get_marker_images(*markers)
	draw_single_marker(ctx, marker_imgs[0], size_in_cm=3.5)
	
	return markers, data, title

def create_paper_from_args(papers, args, ctx):
	if args.type == "video":
		return create_video_paper(papers, args, ctx)
	elif args.type == "portal-in":
		return create_portal_in_paper(papers, args, ctx)
	elif args.type == "portal-out":
		return create_portal_out_paper(papers, args, ctx)
	elif args.type == "gamepad":
		return create_gamepad_paper(papers, args, ctx)
	elif args.type == "python":
		return create_python_paper(papers, args, ctx)
	elif args.type == "shortcut-button":
		return create_shortcut_button_paper(papers, args, ctx)

def main():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(dest="type", required=True)
	
	video_parser = subparsers.add_parser("video")
	video_parser.add_argument("--file", required=True)
	
	subparsers.add_parser("portal-in")
	
	portal_out_parser = subparsers.add_parser("portal-out")
	portal_out_parser.add_argument("--portal-in", required=True)
	
	gamepad_parser = subparsers.add_parser("gamepad")
	gamepad_parser.add_argument("--gamepad-id", type=int, required=True)
	
	python_parser = subparsers.add_parser("python")
	python_parser.add_argument("--filename", required=True)
	
	shortcut_button_parser = subparsers.add_parser("shortcut-button")
	shortcut_button_parser.add_argument("--mqtt-topic", required=True)
	shortcut_button_parser.add_argument("--mqtt-host", required=True)
	
	args = parser.parse_args()
	
	papers = []
	if os.path.exists("papers.json"):
		with open("papers.json", "r") as file:
			papers = json.load(file)
	
	with cairo.PDFSurface("paper.pdf", DIN_A4_WIDTH_POINTS, DIN_A4_HEIGHT_POINTS) as surface:
		ctx = cairo.Context(surface)
		markers, data, title = create_paper_from_args(papers, args, ctx)
	
	papers.append(data)
		
	with open("papers.json", "w") as file:
		json.dump(papers, file, indent=2)
	
	print("created", title)
	print("print paper.pdf")

if __name__ == "__main__":
	main()

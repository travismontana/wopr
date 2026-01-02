import WorkInProgress from "@/components/wip";

export default function ImageView() {
  // TODO: This previously had gameId prop passed in
  // Convert to URL param: /boh/images/view/:gameId
  // Or use query param: /boh/images/view?gameId=xxx
  return <WorkInProgress />;
}

import { useState } from "react";
import { Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import {
  ArrowLeft,
  Shield,
  RefreshCw,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
  Database,
  Activity,
  FileText,
  Settings,
  Loader2,
} from "lucide-react";

export default function Admin() {
  const { user, loading: authLoading } = useAuth();
  const [selectedState, setSelectedState] = useState<string>("");
  
  const { data: dashboardStats, refetch: refetchStats } = trpc.admin.dashboardStats.useQuery(
    undefined,
    { enabled: user?.role === "admin" }
  );
  const { data: stateCodes } = trpc.states.codes.useQuery();
  const { data: recentLogs, refetch: refetchLogs } = trpc.admin.recentLogs.useQuery(
    { limit: 50 },
    { enabled: user?.role === "admin" }
  );
  
  const seedMutation = trpc.admin.seedStates.useMutation({
    onSuccess: () => {
      toast.success("All states seeded successfully!");
      refetchStats();
    },
    onError: (error) => {
      toast.error(`Failed to seed states: ${error.message}`);
    },
  });
  
  const updateStateMutation = trpc.admin.updateState.useMutation({
    onSuccess: (result) => {
      if (result.success) {
        toast.success(`State updated! ${result.changes.length} changes made.`);
      } else {
        toast.error(`Update failed: ${result.error}`);
      }
      refetchStats();
      refetchLogs();
    },
    onError: (error) => {
      toast.error(`Failed to update state: ${error.message}`);
    },
  });
  
  const updateAllMutation = trpc.admin.updateAllStates.useMutation({
    onSuccess: (result) => {
      toast.success(`Update complete! ${result.completed} succeeded, ${result.failed} failed.`);
      refetchStats();
      refetchLogs();
    },
    onError: (error) => {
      toast.error(`Failed to update all states: ${error.message}`);
    },
  });

  // Auth check
  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container py-16 text-center">
          <Shield className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Admin Access Required</h1>
          <p className="text-muted-foreground mb-6">Please sign in to access the admin dashboard.</p>
          <a href={getLoginUrl()}>
            <Button>Sign In</Button>
          </a>
        </div>
      </div>
    );
  }

  if (user.role !== "admin") {
    return (
      <div className="min-h-screen bg-background">
        <div className="container py-16 text-center">
          <AlertCircle className="h-16 w-16 text-destructive mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Access Denied</h1>
          <p className="text-muted-foreground mb-6">You don't have permission to access the admin dashboard.</p>
          <Link href="/">
            <Button variant="outline">Return Home</Button>
          </Link>
        </div>
      </div>
    );
  }

  const isUpdating = updateStateMutation.isPending || updateAllMutation.isPending;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="sm" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <Settings className="h-6 w-6 text-primary" />
              <span className="font-semibold">Admin Dashboard</span>
            </div>
          </div>
          <div className="text-sm text-muted-foreground">
            Signed in as {user.name || user.email}
          </div>
        </div>
      </header>

      <main className="container py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Database className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-2xl font-bold">{dashboardStats?.totalStates || 0}</p>
                  <p className="text-sm text-muted-foreground">Total States</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-8 w-8 text-green-600" />
                <div>
                  <p className="text-2xl font-bold">{dashboardStats?.statusCounts?.active || 0}</p>
                  <p className="text-sm text-muted-foreground">Active Programs</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Activity className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold">{dashboardStats?.recentLogs?.length || 0}</p>
                  <p className="text-sm text-muted-foreground">Recent Updates</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Clock className="h-8 w-8 text-orange-600" />
                <div>
                  <p className="text-2xl font-bold">
                    {dashboardStats?.lastUpdated 
                      ? new Date(dashboardStats.lastUpdated).toLocaleDateString()
                      : "Never"
                    }
                  </p>
                  <p className="text-sm text-muted-foreground">Last Updated</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="actions" className="space-y-6">
          <TabsList>
            <TabsTrigger value="actions">Actions</TabsTrigger>
            <TabsTrigger value="logs">Update Logs</TabsTrigger>
            <TabsTrigger value="runs">Update Runs</TabsTrigger>
          </TabsList>

          {/* Actions Tab */}
          <TabsContent value="actions" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Seed States */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Initialize Database
                  </CardTitle>
                  <CardDescription>
                    Seed the database with initial data for all 51 states (50 states + DC).
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    onClick={() => seedMutation.mutate()}
                    disabled={seedMutation.isPending}
                    className="w-full"
                  >
                    {seedMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Seeding...
                      </>
                    ) : (
                      <>
                        <Database className="h-4 w-4 mr-2" />
                        Seed All States
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Update Single State */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <RefreshCw className="h-5 w-5" />
                    Update Single State
                  </CardTitle>
                  <CardDescription>
                    Trigger an update for a specific state using LLM extraction.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Select value={selectedState} onValueChange={setSelectedState}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a state" />
                    </SelectTrigger>
                    <SelectContent>
                      {stateCodes?.map((state) => (
                        <SelectItem key={state.code} value={state.code}>
                          {state.code} - {state.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button 
                    onClick={() => {
                      if (selectedState) {
                        updateStateMutation.mutate({ code: selectedState });
                      }
                    }}
                    disabled={!selectedState || isUpdating}
                    className="w-full"
                  >
                    {updateStateMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Updating...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Update State
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Update All States */}
              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Play className="h-5 w-5" />
                    Run Weekly Update
                  </CardTitle>
                  <CardDescription>
                    Trigger a full update for all 51 states. This process takes approximately 2-4 hours 
                    with a 2-second delay between states to avoid rate limiting.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4">
                    <Button 
                      onClick={() => updateAllMutation.mutate()}
                      disabled={isUpdating}
                      size="lg"
                    >
                      {updateAllMutation.isPending ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Running Update...
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-2" />
                          Start Full Update
                        </>
                      )}
                    </Button>
                    {dashboardStats?.activeRun && (
                      <Badge variant="secondary" className="gap-2">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Update in progress: {dashboardStats.activeRun.completedStates}/{dashboardStats.activeRun.totalStates}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Recent Update Logs
                </CardTitle>
                <CardDescription>
                  View the history of all data updates and changes.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {recentLogs && recentLogs.length > 0 ? (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>State</TableHead>
                          <TableHead>Field</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Date</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {recentLogs.map((log) => (
                          <TableRow key={log.id}>
                            <TableCell className="font-medium">{log.stateCode}</TableCell>
                            <TableCell>{log.fieldChanged}</TableCell>
                            <TableCell>
                              <Badge 
                                variant={log.status === "success" ? "default" : "destructive"}
                                className="gap-1"
                              >
                                {log.status === "success" ? (
                                  <CheckCircle2 className="h-3 w-3" />
                                ) : (
                                  <XCircle className="h-3 w-3" />
                                )}
                                {log.status}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline">{log.updateType}</Badge>
                            </TableCell>
                            <TableCell className="text-muted-foreground">
                              {new Date(log.createdAt).toLocaleString()}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No update logs yet. Run an update to see logs here.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Runs Tab */}
          <TabsContent value="runs">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Update Run History
                </CardTitle>
                <CardDescription>
                  View the history of batch update operations.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {dashboardStats?.recentRuns && dashboardStats.recentRuns.length > 0 ? (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Run ID</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Progress</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Started</TableHead>
                          <TableHead>Completed</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {dashboardStats.recentRuns.map((run) => (
                          <TableRow key={run.id}>
                            <TableCell className="font-medium">#{run.id}</TableCell>
                            <TableCell>
                              <Badge variant="outline">{run.runType}</Badge>
                            </TableCell>
                            <TableCell>
                              {run.completedStates}/{run.totalStates} 
                              {run.failedStates > 0 && (
                                <span className="text-destructive ml-1">
                                  ({run.failedStates} failed)
                                </span>
                              )}
                            </TableCell>
                            <TableCell>
                              <Badge 
                                variant={
                                  run.status === "completed" ? "default" : 
                                  run.status === "running" ? "secondary" : "destructive"
                                }
                              >
                                {run.status}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-muted-foreground">
                              {new Date(run.startedAt).toLocaleString()}
                            </TableCell>
                            <TableCell className="text-muted-foreground">
                              {run.completedAt 
                                ? new Date(run.completedAt).toLocaleString()
                                : "-"
                              }
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No update runs yet. Start a full update to see run history.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
